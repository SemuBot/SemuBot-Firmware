/*
 * motor.c
 *
 *  Created on: Nov 18, 2024
 *      Author: medved
 */


#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "motor.h"
#include "tim.h"
#include "stm32f3xx_hal.h"
#include "usart.h"



static uint8_t duty_cycle_limit;



motor_st motor1 = {
	.dir_port = motor1_dir_GPIO_Port,
	.dir_pin = motor1_dir_Pin,
    .pwm_timer = &htim1,
    .pwm_port = motor1_pwm_GPIO_Port,
    .pwm_pin = motor1_pwm_Pin,
	.led_port =motor1_led_GPIO_Port,
	.led_pin = motor1_led_Pin,
    .duty_cycle = 0.0,
	.duty_cycle_limit = DUTY_CYCLE_LIMIT

};

motor_st motor2 = {
	.dir_port = motor2_dir_GPIO_Port,
	.dir_pin = motor2_dir_Pin,
    .pwm_timer = &htim3,
    .pwm_port = motor2_pwm_GPIO_Port,
    .pwm_pin = motor2_pwm_Pin,
	.led_port = motor2_led_GPIO_Port,
	.led_pin = motor2_led_Pin,
    .duty_cycle = 0.0,
	.duty_cycle_limit = DUTY_CYCLE_LIMIT

};

motor_st motor3 = {
	.dir_port = motor3_dir_GPIO_Port,
	.dir_pin = motor3_dir_Pin,
    .pwm_timer = &htim4,
    .pwm_port = motor3_pwm_GPIO_Port,
    .pwm_pin = motor3_pwm_Pin,
	.led_port = motor3_led_GPIO_Port,
	.led_pin = motor3_led_Pin,
    .duty_cycle = 0.0,
	.duty_cycle_limit = DUTY_CYCLE_LIMIT
};



void motor_init(motor_st *motor_data){
    duty_cycle_limit = DUTY_CYCLE_LIMIT_DEFAULT;
    motor_disable(motor_data);
}



void motor_update(motor_st *motor_data)
{
    uint16_t scaled_duty_cycle;
    uint16_t arr_value = __HAL_TIM_GET_AUTORELOAD(motor_data->pwm_timer);

    static uint32_t led_blink_counter = 0;


    // Check if the motor is enabled
    if (motor_data->duty_cycle >= 0)
    {
        motor_enable(motor_data);
        HAL_GPIO_WritePin(motor_data->dir_port, motor_data->dir_pin, GPIO_PIN_SET);
        // LED on solid- forward
        HAL_GPIO_WritePin(motor_data->led_port, motor_data->led_pin, GPIO_PIN_SET);
    }
    else if (motor_data->duty_cycle < 0)
    {
        HAL_GPIO_WritePin(motor_data->dir_port, motor_data->dir_pin, GPIO_PIN_RESET);
        motor_enable(motor_data);
        // LED OFF - reverse direction
        HAL_GPIO_WritePin(motor_data->led_port, motor_data->led_pin, GPIO_PIN_RESET);
    }
    else
    {
        motor_disable(motor_data);
        // LED blinking, not moving
        if (++led_blink_counter > 1000) {
            HAL_GPIO_TogglePin(motor_data->led_port, motor_data->led_pin);
            led_blink_counter = 0;
        }
        return;
    }

    // Scale the duty cycle based on the motor's duty cycle
    scaled_duty_cycle = (uint16_t)((fabs(motor_data->duty_cycle) / 100.0f) * arr_value);
    if (scaled_duty_cycle > arr_value)
    {
        scaled_duty_cycle = arr_value;
    }

    __HAL_TIM_SET_COMPARE(motor_data->pwm_timer, TIM_CHANNEL_1, scaled_duty_cycle);

}



void calculate_motor_duty_cycles(float linear_x, float linear_y, float omega, motor_st *motor1, motor_st *motor2, motor_st *motor3) {

    float duty_cycle_1 = (linear_x * cosf(motor1_angle) + linear_y * sinf(motor1_angle) + (omega * ROBOT_RADIUS)) * PWM_SCALING_FACTOR;
    float duty_cycle_2 = (linear_x * cosf(motor2_angle) + linear_y * sinf(motor2_angle) + (omega * ROBOT_RADIUS)) * PWM_SCALING_FACTOR;
    float duty_cycle_3 = (linear_x * cosf(motor3_angle) + linear_y * sinf(motor3_angle) + (omega * ROBOT_RADIUS)) * PWM_SCALING_FACTOR;

    duty_cycle_1 = fmaxf(-100.0f, fminf(100.0f, duty_cycle_1));
    duty_cycle_2 = fmaxf(-100.0f, fminf(100.0f, duty_cycle_2));
    duty_cycle_3 = fmaxf(-100.0f, fminf(100.0f, duty_cycle_3));

    motor1->duty_cycle = duty_cycle_1;
    motor2->duty_cycle = duty_cycle_2;
    motor3->duty_cycle = duty_cycle_3;

    motor_update(motor1);
    motor_update(motor2);
    motor_update(motor3);
}


void motor_enable(motor_st *motor_data){
    HAL_TIM_PWM_Start(motor_data->pwm_timer, TIM_CHANNEL_1);
}


void motor_disable(motor_st *motor_data){
    HAL_TIM_PWM_Stop(motor_data->pwm_timer, TIM_CHANNEL_1);
}

