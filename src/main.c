/* Educational FreeRTOS spacecraft communication simulator for Linux GCC_POSIX. */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <stdatomic.h>
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

typedef enum { LAUNCH, ASCENT, ORBIT_INSERTION } Phase;
typedef enum { DYNAMIC, STATIC, EQUAL, INVERTED } Policy;
typedef struct { TickType_t created; unsigned id; Phase phase; } Message;
typedef struct {
  TickType_t tick;
  Phase phase;
  const char *channel, *event;
  unsigned depth, latency, deadline;
} Event;

static QueueHandle_t telemetryQ, commandQ, emergencyQ, eventQ;
static TaskHandle_t telemetryWorkerHandle, commandWorkerHandle;
static atomic_int phaseNow = ATOMIC_VAR_INIT(LAUNCH);
static atomic_int stopProducers = ATOMIC_VAR_INIT(0);
static atomic_int stopWorkers = ATOMIC_VAR_INIT(0);
static atomic_int stopLogger = ATOMIC_VAR_INIT(0);
static atomic_uint sentT, sentC, sentE, doneT, doneC, doneE;
static atomic_uint dropT, dropC, dropE, dropLog;
static TickType_t epoch;
static unsigned duration = 30, depth = 16, stress = 1, emergencyInterval = 3000;
static unsigned serviceUs = 0; /* Optional measured host-thread CPU demand. */
static char runId[48] = "run1";
static Policy policy = DYNAMIC;

static const char *phaseName(Phase p) {
  return p == LAUNCH ? "LAUNCH" : p == ASCENT ? "ASCENT" : "ORBIT_INSERTION";
}
static void logEvent(Phase p, const char *channel, const char *event,
                     unsigned qdepth, unsigned latency, unsigned deadline) {
  Event e = {xTaskGetTickCount() - epoch, p, channel, event, qdepth, latency, deadline};
  if(xQueueSend(eventQ, &e, 0) != pdTRUE) atomic_fetch_add(&dropLog, 1);
}
static unsigned telemetryPeriod(Phase p) {
  return p == LAUNCH ? 50 : p == ASCENT ? 100 : 40;
}
static unsigned commandPeriod(Phase p) {
  return p == LAUNCH ? 160 : p == ASCENT ? 60 : 100;
}
static void burn(unsigned units) {
  volatile uint32_t x = 1;
  for(unsigned i = 0; i < units * 1000u; i++) x = (x ^ i) * 1664525u + 1013904223u;
  (void)x;
}
/* CPU time excludes time when this POSIX task thread is suspended. The
 * optional demand exposes contention hidden by the small default loop. */
static void service(unsigned multiplier) {
  if(!serviceUs) return;
  struct timespec start, now;
  if(clock_gettime(CLOCK_THREAD_CPUTIME_ID, &start)) { perror("clock_gettime"); exit(2); }
  int64_t target = (int64_t)serviceUs * multiplier * 1000;
  do {
    burn(1);
    if(clock_gettime(CLOCK_THREAD_CPUTIME_ID, &now)) { perror("clock_gettime"); exit(2); }
  } while(((int64_t)now.tv_sec - start.tv_sec) * 1000000000LL + now.tv_nsec - start.tv_nsec < target);
}
static void produceTelemetry(void *arg) {
  (void)arg;
  unsigned id = 0;
  while(!atomic_load(&stopProducers)) {
    Phase p = (Phase)atomic_load(&phaseNow);
    Message msg = {xTaskGetTickCount(), ++id, p};
    if(xQueueSend(telemetryQ, &msg, 0) == pdTRUE) atomic_fetch_add(&sentT, 1);
    else {
      atomic_fetch_add(&dropT, 1);
      logEvent(p, "telemetry", "dropped", uxQueueMessagesWaiting(telemetryQ), 0, 100);
    }
    vTaskDelay(pdMS_TO_TICKS(telemetryPeriod(p)));
  }
  vTaskDelete(NULL);
}
static void produceCommand(void *arg) {
  (void)arg;
  unsigned id = 0;
  while(!atomic_load(&stopProducers)) {
    Phase p = (Phase)atomic_load(&phaseNow);
    Message msg = {xTaskGetTickCount(), ++id, p};
    if(xQueueSend(commandQ, &msg, 0) == pdTRUE) atomic_fetch_add(&sentC, 1);
    else {
      atomic_fetch_add(&dropC, 1);
      logEvent(p, "command", "dropped", uxQueueMessagesWaiting(commandQ), 0, 80);
    }
    vTaskDelay(pdMS_TO_TICKS(commandPeriod(p)));
  }
  vTaskDelete(NULL);
}
static void injectEmergency(void *arg) {
  (void)arg;
  unsigned id = 0;
  while(!atomic_load(&stopProducers)) {
    vTaskDelay(pdMS_TO_TICKS(emergencyInterval));
    if(atomic_load(&stopProducers)) break;
    Phase p = (Phase)atomic_load(&phaseNow);
    Message msg = {xTaskGetTickCount(), ++id, p};
    if(xQueueSend(emergencyQ, &msg, 0) == pdTRUE) atomic_fetch_add(&sentE, 1);
    else {
      atomic_fetch_add(&dropE, 1);
      logEvent(p, "emergency", "dropped", uxQueueMessagesWaiting(emergencyQ), 0, 20);
    }
  }
  vTaskDelete(NULL);
}
static void processTelemetry(void *arg) {
  (void)arg;
  Message msg;
  while(!atomic_load(&stopWorkers) || uxQueueMessagesWaiting(telemetryQ)) {
    if(xQueueReceive(telemetryQ, &msg, pdMS_TO_TICKS(20)) == pdTRUE) {
      burn(stress * (msg.phase == ORBIT_INSERTION ? 4u : 2u));
      service(msg.phase == ORBIT_INSERTION ? 2u : 1u);
      unsigned elapsed = (unsigned)(xTaskGetTickCount() - msg.created);
      atomic_fetch_add(&doneT, 1);
      logEvent(msg.phase, "telemetry", elapsed > 100 ? "deadline_miss" : "completed",
               uxQueueMessagesWaiting(telemetryQ), elapsed, 100);
    }
  }
  vTaskDelete(NULL);
}
static void processCommand(void *arg) {
  (void)arg;
  Message msg;
  while(!atomic_load(&stopWorkers) || uxQueueMessagesWaiting(commandQ)) {
    if(xQueueReceive(commandQ, &msg, pdMS_TO_TICKS(20)) == pdTRUE) {
      burn(stress * 2u);
      service(1u);
      unsigned elapsed = (unsigned)(xTaskGetTickCount() - msg.created);
      atomic_fetch_add(&doneC, 1);
      logEvent(msg.phase, "command", elapsed > 80 ? "deadline_miss" : "completed",
               uxQueueMessagesWaiting(commandQ), elapsed, 80);
    }
  }
  vTaskDelete(NULL);
}
static void processEmergency(void *arg) {
  (void)arg;
  Message msg;
  while(!atomic_load(&stopWorkers) || uxQueueMessagesWaiting(emergencyQ)) {
    if(xQueueReceive(emergencyQ, &msg, pdMS_TO_TICKS(20)) == pdTRUE) {
      unsigned elapsed = (unsigned)(xTaskGetTickCount() - msg.created);
      atomic_fetch_add(&doneE, 1);
      logEvent(msg.phase, "emergency", elapsed > 20 ? "deadline_miss" : "handled",
               uxQueueMessagesWaiting(emergencyQ), elapsed, 20);
    }
  }
  vTaskDelete(NULL);
}
static void setPolicy(Phase p) {
  UBaseType_t t = 3, c = 2;
  if(policy == DYNAMIC && p == ASCENT) { t = 2; c = 3; }
  else if(policy == EQUAL) { t = 2; c = 2; }
  else if(policy == INVERTED) { t = 1; c = 4; }
  vTaskPrioritySet(telemetryWorkerHandle, t);
  vTaskPrioritySet(commandWorkerHandle, c);
  logEvent(p, "phase", "priority_update", 0, (unsigned)t, (unsigned)c);
}
static void managePhase(void *arg) {
  (void)arg;
  Phase old = LAUNCH;
  setPolicy(old);
  while(!atomic_load(&stopProducers)) {
    TickType_t elapsed = xTaskGetTickCount() - epoch;
    unsigned third = duration * 1000u / 3u;
    Phase p = elapsed >= pdMS_TO_TICKS(third * 2u) ? ORBIT_INSERTION :
              elapsed >= pdMS_TO_TICKS(third) ? ASCENT : LAUNCH;
    if(p != old) {
      atomic_store(&phaseNow, p);
      old = p;
      logEvent(p, "phase", "transition", 0, 0, 0);
      setPolicy(p);
    }
    vTaskDelay(pdMS_TO_TICKS(10));
  }
  vTaskDelete(NULL);
}
static void monitorQueues(void *arg) {
  (void)arg;
  while(!atomic_load(&stopWorkers)) {
    Phase p = (Phase)atomic_load(&phaseNow);
    logEvent(p, "monitor", "telemetry_depth", uxQueueMessagesWaiting(telemetryQ), 0, 0);
    logEvent(p, "monitor", "command_depth", uxQueueMessagesWaiting(commandQ), 0, 0);
    logEvent(p, "monitor", "emergency_depth", uxQueueMessagesWaiting(emergencyQ), 0, 0);
    vTaskDelay(pdMS_TO_TICKS(250));
  }
  vTaskDelete(NULL);
}
static void logToCsv(void *arg) {
  (void)arg;
  Event e;
  while(!atomic_load(&stopLogger) || uxQueueMessagesWaiting(eventQ)) {
    if(xQueueReceive(eventQ, &e, pdMS_TO_TICKS(20)) == pdTRUE)
      printf("%s,%lu,%s,%s,%s,%u,%u,%u\n", runId, (unsigned long)e.tick,
             phaseName(e.phase), e.channel, e.event, e.depth, e.latency, e.deadline);
  }
  fflush(stdout);
  vTaskDelete(NULL);
}
static void finishMission(void *arg) {
  (void)arg;
  vTaskDelay(pdMS_TO_TICKS(duration * 1000u));
  atomic_store(&stopProducers, 1);
  /* Give sources one complete wakeup cycle, including emergency producer. */
  vTaskDelay(pdMS_TO_TICKS(emergencyInterval + 100u));
  TickType_t cutoff = xTaskGetTickCount() + pdMS_TO_TICKS(1500);
  while((uxQueueMessagesWaiting(telemetryQ) || uxQueueMessagesWaiting(commandQ) ||
         uxQueueMessagesWaiting(emergencyQ)) && xTaskGetTickCount() < cutoff)
    vTaskDelay(pdMS_TO_TICKS(20));
  atomic_store(&stopWorkers, 1);
  vTaskDelay(pdMS_TO_TICKS(200));
  logEvent((Phase)atomic_load(&phaseNow), "mission", "finished", 0, 0, 0);
  cutoff = xTaskGetTickCount() + pdMS_TO_TICKS(2000);
  while(uxQueueMessagesWaiting(eventQ) && xTaskGetTickCount() < cutoff)
    vTaskDelay(pdMS_TO_TICKS(20));
  atomic_store(&stopLogger, 1);
  vTaskDelay(pdMS_TO_TICKS(100));
  fprintf(stderr, "COUNTS sent_tel=%u processed_tel=%u dropped_tel=%u sent_cmd=%u processed_cmd=%u dropped_cmd=%u sent_emg=%u processed_emg=%u dropped_emg=%u dropped_log=%u remaining=%u/%u/%u/%u\n",
          atomic_load(&sentT), atomic_load(&doneT), atomic_load(&dropT),
          atomic_load(&sentC), atomic_load(&doneC), atomic_load(&dropC),
          atomic_load(&sentE), atomic_load(&doneE), atomic_load(&dropE),
          atomic_load(&dropLog), uxQueueMessagesWaiting(telemetryQ),
          uxQueueMessagesWaiting(commandQ), uxQueueMessagesWaiting(emergencyQ),
          uxQueueMessagesWaiting(eventQ));
  fflush(stderr);
  /* POSIX-only process termination: not a hardware-safe shutdown strategy. */
  exit(0);
}
void vProjectAssert(const char *file, int line) {
  fprintf(stderr, "ASSERT: %s:%d\n", file, line); abort();
}
void vApplicationStackOverflowHook(TaskHandle_t task, char *name) {
  (void)task; fprintf(stderr, "STACK OVERFLOW: %s\n", name); abort();
}
void vApplicationMallocFailedHook(void) {
  fputs("MALLOC FAILED\n", stderr); abort();
}
static void create(TaskFunction_t fn, const char *name, UBaseType_t priority, TaskHandle_t *handle) {
  if(xTaskCreate(fn, name, 2048, NULL, priority, handle) != pdPASS) {
    fprintf(stderr, "Task creation failed: %s\n", name); exit(2);
  }
}
static unsigned number(const char *s, unsigned min, unsigned max) {
  char *end = NULL;
  errno = 0;
  unsigned long v = strtoul(s, &end, 10);
  if(errno || s == end || *end != '\0' || v < min || v > max) {
    fprintf(stderr, "Invalid numeric option: %s\n", s); exit(2);
  }
  return (unsigned)v;
}
int main(int argc, char **argv) {
  for(int i = 1; i < argc; ++i) {
    if(!strcmp(argv[i], "--policy") && i + 1 < argc) {
      const char *p = argv[++i];
      if(!strcmp(p, "dynamic")) policy = DYNAMIC;
      else if(!strcmp(p, "static")) policy = STATIC;
      else if(!strcmp(p, "equal")) policy = EQUAL;
      else if(!strcmp(p, "inverted")) policy = INVERTED;
      else { fprintf(stderr, "Unknown policy: %s\n", p); return 2; }
    } else if(!strcmp(argv[i], "--duration") && i + 1 < argc)
      duration = number(argv[++i], 9, 3600);
    else if(!strcmp(argv[i], "--telemetry-queue") && i + 1 < argc)
      depth = number(argv[++i], 1, 256);
    else if(!strcmp(argv[i], "--stress") && i + 1 < argc)
      stress = number(argv[++i], 1, 1000);
    else if(!strcmp(argv[i], "--service-us") && i + 1 < argc)
      serviceUs = number(argv[++i], 0, 1000000);
    else if(!strcmp(argv[i], "--emergency-interval") && i + 1 < argc)
      emergencyInterval = number(argv[++i], 100, 3000);
    else if(!strcmp(argv[i], "--run-id") && i + 1 < argc) {
      const char *id = argv[++i];
      if(!*id || strlen(id) >= sizeof(runId) ||
         strspn(id, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-") != strlen(id)) {
        fputs("Run ID must contain only letters, digits, underscore or dash\n", stderr); return 2;
      }
      strcpy(runId, id);
    } else {
      fprintf(stderr, "Unknown or incomplete option: %s\n", argv[i]); return 2;
    }
  }
  setvbuf(stdout, NULL, _IOLBF, 0);
  telemetryQ = xQueueCreate(depth, sizeof(Message));
  commandQ = xQueueCreate(16, sizeof(Message));
  emergencyQ = xQueueCreate(8, sizeof(Message));
  eventQ = xQueueCreate(1024, sizeof(Event));
  if(!telemetryQ || !commandQ || !emergencyQ || !eventQ) {
    fputs("Queue allocation failed\n", stderr); return 2;
  }
  puts("run_id,tick,phase,channel,event,queue_depth,latency_ticks,deadline_ticks");
  epoch = xTaskGetTickCount();
  create(processTelemetry, "TelemetryWorker", 3, &telemetryWorkerHandle);
  create(processCommand, "CommandWorker", 2, &commandWorkerHandle);
  create(processEmergency, "EmergencyWorker", 5, NULL);
  create(managePhase, "PhaseManager", 4, NULL);
  create(produceTelemetry, "TelemetrySource", 2, NULL);
  create(produceCommand, "GroundSource", 2, NULL);
  create(injectEmergency, "FaultSource", 2, NULL);
  create(monitorQueues, "QueueMonitor", 1, NULL);
  create(logToCsv, "Logger", 1, NULL);
  create(finishMission, "MissionEnd", 6, NULL);
  vTaskStartScheduler();
  fputs("Scheduler returned unexpectedly\n", stderr);
  return 3;
}
