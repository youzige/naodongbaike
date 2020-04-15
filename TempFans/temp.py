#!/usr/bin/python3.7
#coding:utf-8

from RPi import GPIO as gpio
import time
import sys

#获取cpu的温度
def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
        temp = float(f.read()) / 1000
    return temp

#log输出
def log_message(message):
    f = open("/home/pi/Documents/run/templog", 'a+')
    f.seek(0, 2)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    f.write(current_time + " [Log] ")
    f.write(message)
    f.write("\n")
    #f.close()

temp_check_interval = 10 #温度检测间隔，单位：秒
temp_hot = 55  #风扇开启的温度
temp_cool = 40 #风扇关闭的温度

#监控CPU温度，控制风扇开关
def check_temp(port):
    #关闭警告输出
    gpio.setwarnings(False)
    #设置BOARD编号方式，.BOARD为基于插座引脚物理编号
    gpio.setmode(gpio.BOARD)
    
    #设置指定引脚为输出模式
    gpio.setup(port, gpio.OUT)
    
    #标记风扇开关状态
    is_fans_open = False
    
    #先关闭风扇，防止长转不停。
    gpio.output(port, 0)
    
    try:
        while True:
            temp = get_cpu_temp()
            if is_fans_open==False:
                #温度大于等于上限时，使引脚输出高电平
                if temp>=temp_hot:
                    gpio.output(port, 1)
                    is_fans_open = True
                    log_message("Fans turn on. Now temp is %s" % temp)
            else:
                #温度降低到下限极其以下时，使引脚输出低电平
                if temp<=temp_cool:
                    gpio.output(port, 0)
                    is_fans_open = False
                    log_message("Fans turn off. Now temp is %s" % temp)
            #sleep
            time.sleep(temp_check_interval)
    except Exception as e:
        gpio.cleanup()
        #print(e)
        log_message("%s" % e)

if __name__ == '__main__':
    port = 16
    log_message("CPU temp guardian actived!")
    log_message("GPIO.port = %s current_temp = %s " %(port, get_cpu_temp()))
    check_temp(port)
