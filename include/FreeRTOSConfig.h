#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H
#include <stdint.h>
#include <stddef.h>
#define configUSE_PREEMPTION 1
#define configUSE_TIME_SLICING 1
#define configCPU_CLOCK_HZ ( ( unsigned long ) 1000000000UL )
#define configTICK_RATE_HZ ( ( TickType_t ) 1000 )
#define configMAX_PRIORITIES 7
#define configMINIMAL_STACK_SIZE 256
#define configTOTAL_HEAP_SIZE ( ( size_t ) ( 1024 * 1024 ) )
#define configMAX_TASK_NAME_LEN 24
#define configUSE_16_BIT_TICKS 0
#define configUSE_IDLE_HOOK 0
#define configUSE_TICK_HOOK 0
#define configIDLE_SHOULD_YIELD 1
#define configUSE_MUTEXES 1
#define configUSE_RECURSIVE_MUTEXES 0
#define configUSE_COUNTING_SEMAPHORES 1
#define configQUEUE_REGISTRY_SIZE 8
#define configCHECK_FOR_STACK_OVERFLOW 2
#define configUSE_MALLOC_FAILED_HOOK 1
#define configUSE_TRACE_FACILITY 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configSUPPORT_STATIC_ALLOCATION 0
#define configUSE_TIMERS 0
#define INCLUDE_vTaskDelay 1
#define INCLUDE_vTaskDelayUntil 1
#define INCLUDE_vTaskPrioritySet 1
#define INCLUDE_vTaskDelete 1
#define INCLUDE_xTaskGetCurrentTaskHandle 1
#define INCLUDE_uxTaskGetStackHighWaterMark 1
void vProjectAssert(const char *file, int line);
#define configASSERT(x) do { if (!(x)) vProjectAssert(__FILE__,__LINE__); } while (0)
#endif
