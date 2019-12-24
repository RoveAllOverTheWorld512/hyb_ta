# -*- coding: utf-8 -*-
"""
Created on 2019-12-02 10:48:17

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""
 
import pythoncom
import pyHook
import time
import pyhk
import os
import sys
import ctypes
from ctypes import wintypes
import win32con
 
 
class CInspectKeyAndMouseEvent:
    '''
    Function:键盘和鼠标监控类
    Input：NONE
    Output: NONE
    author: socrates
    blog:http://blog.csdn.net/dyx1024
    date:2012-03-09
    ''' 
    def __init__(self, filename):
        self.filename = filename
        
    def open_file(self):
        self.fobj = open(self.filename,  'w') 
        
    def close_file(self):
        self.fobj.close()    
        
    def onMouseEvent(self, event):      
        "处理鼠标事件"
        self.fobj.writelines('-' * 20 + 'MouseEvent Begin' + '-' * 20 + '\n')
        self.fobj.writelines("Current Time:%s\n" % time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
        self.fobj.writelines("MessageName:%s\n" % str(event.MessageName))
        self.fobj.writelines("Message:%d\n" % event.Message)
        self.fobj.writelines("Time_sec:%d\n" % event.Time)
        self.fobj.writelines("Window:%s\n" % str(event.Window))
        self.fobj.writelines("WindowName:%s\n" % str(event.WindowName))
        self.fobj.writelines("Position:%s\n" % str(event.Position))
        self.fobj.writelines('-' * 20 + 'MouseEvent End' + '-' * 20 + '\n')
        return True
    
    def onKeyboardEvent(self, event): 
        "处理键盘事件"   
        self.fobj.writelines('-' * 20 + 'Keyboard Begin' + '-' * 20 + '\n')
        self.fobj.writelines("Current Time:%s\n" % time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
        self.fobj.writelines("MessageName:%s\n" % str(event.MessageName))
        self.fobj.writelines("Message:%d\n" % event.Message)
        self.fobj.writelines("Time:%d\n" % event.Time)
        self.fobj.writelines("Window:%s\n" % str(event.Window))
        self.fobj.writelines("WindowName:%s\n" % str(event.WindowName))
        self.fobj.writelines("Ascii_code: %d\n" % event.Ascii)
        self.fobj.writelines("Ascii_char:%s\n" % chr(event.Ascii))
        self.fobj.writelines("Key:%s\n" % str(event.Key))
        self.fobj.writelines('-' * 20 + 'Keyboard End' + '-' * 20 + '\n')
        return True
 
def InspectKeyAndMouseEvent(bRunTag = False):
    ""
    if bRunTag:
        my_event = CInspectKeyAndMouseEvent("D:\\hook_log.txt")
        my_event.open_file()
     
        #创建hook句柄
        hm = pyHook.HookManager()
 
        #监控键盘
        hm.KeyDown = my_event.onKeyboardEvent
        hm.HookKeyboard()
 
        #监控鼠标
        hm.MouseAll = my_event.onMouseEvent
        hm.HookMouse()
    
        #循环获取消息
        pythoncom.PumpMessages()
        my_event.close_file() 
    else:  #程序走不到这里，直接在PumpMessages处不停地监听
        os._exit(0)                
     
def handle_start_InspecEvent():
    "开始监控（按下Ctrl + F3）"
    InspectKeyAndMouseEvent(True)
 
def handle_stop_InspecEvent():
    "停止监控  (按下Ctrl + F4)"
    InspectKeyAndMouseEvent(False)   
        
          
if __name__ == "__main__":     
    '''
    Function:通过快捷键控制程序运行
    Input：NONE
    Output: NONE
    author: socrates
    blog:http://blog.csdn.net/dyx1024
    date:2012-03-09
    '''  
    
    byref = ctypes.byref
    user32 = ctypes.windll.user32
    
    #定义快捷键
    HOTKEYS = {
               1 : (win32con.VK_F3, win32con.MOD_CONTROL),
               2 : (win32con.VK_F4, win32con.MOD_CONTROL)
               }
 
    #快捷键对应的驱动函数
    HOTKEY_ACTIONS = {
        1 : handle_start_InspecEvent,
        2 : handle_stop_InspecEvent
        }    
 
    #注册快捷键
    for id, (vk, modifiers) in HOTKEYS.items ():
        if not user32.RegisterHotKey (None, id, modifiers, vk):
            print("Unable to register id", id)    
    
    #启动监听        
    try:
        msg = wintypes.MSG ()
        while user32.GetMessageA (byref (msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                action_to_take = HOTKEY_ACTIONS.get (msg.wParam)
                if action_to_take:
                    action_to_take ()
 
            user32.TranslateMessage (byref (msg))
            user32.DispatchMessageA (byref (msg))
 
    finally:
        for id in HOTKEYS.keys ():
            user32.UnregisterHotKey (None, id)
