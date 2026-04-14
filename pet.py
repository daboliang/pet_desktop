import tkinter
import os
import random
from platform import system


class Pet:

    def __init__(self):
        self.root = tkinter.Tk()  # create window
        self.delay = 200  # delay in ms
        self.pixels_from_right = 200  # change to move the pet's starting position
        self.pixels_from_bottom = 200  # change to move the pet's starting position
        self.move_speed = 6  # change how fast the pet moves in pixels
        self.current_animation = 'idle'  # 当前动画状态
        self.drag_data = {"x": 0, "y": 0}  # 拖拽数据
        self.after_id = None  # 用于存储after方法的返回值，以便取消任务

        # initialize frame arrays
        self.animation = dict(
            idle=[tkinter.PhotoImage(file=os.path.abspath('gifs/idle.gif'), format='gif -index %i' % i) for i in range(5)],
            idle_to_sleep=[tkinter.PhotoImage(file=os.path.abspath('gifs/idle-to-sleep.gif'), format='gif -index %i' % i) for i in range(8)],
            sleep=[tkinter.PhotoImage(file=os.path.abspath('gifs/sleep.gif'), format='gif -index %i' % i) for i in range(3)] * 3,
            sleep_to_idle=[tkinter.PhotoImage(file=os.path.abspath('gifs/sleep-to-idle.gif'), format='gif -index %i' % i) for i in range(8)],
            walk_left=[tkinter.PhotoImage(file=os.path.abspath('gifs/walk-left.gif'), format='gif -index %i' % i) for i in range(8)],
            walk_right=[tkinter.PhotoImage(file=os.path.abspath('gifs/walk-right.gif'), format='gif -index %i' % i) for i in range(8)]
        )

        # window configuration
        self.root.overrideredirect(True)  # remove UI
        if system() == 'Windows':
            self.root.wm_attributes('-transparent', 'black')
        else:  # platform is Mac/Linux
            # https://stackoverflow.com/questions/19080499/transparent-background-in-a-tkinter-window
            self.root.wm_attributes('-transparent', True)  # do this for mac, but the bg stays black
            self.root.config(bg='systemTransparent')

        self.root.attributes('-topmost', True)  # put window on top
        self.root.bind("<Button-1>", self.onLeftClick)
        self.root.bind("<Button-2>", self.show_context_menu)
        self.root.bind("<Button-3>", self.show_context_menu)
        # 鼠标进入和离开事件
        self.root.bind("<Enter>", self.on_enter)
        self.root.bind("<Leave>", self.on_leave)
        # 拖拽事件
        self.root.bind("<ButtonPress-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.label = tkinter.Label(self.root, bd=0, bg='black')  # borderless window
        if system() != 'Windows':
            self.label.config(bg='systemTransparent')
        self.label.pack()

        screen_width = self.root.winfo_screenwidth()  # width of the entire screen
        screen_height = self.root.winfo_screenheight()  # height of the entire screen
        self.min_width = 10  # do not let the pet move beyond this point
        self.max_width = screen_width - 110  # do not let the pet move beyond this point
        self.min_height = 10  # 最小高度
        self.max_height = screen_height - 110  # 最大高度

        # change starting properties of the window
        self.curr_width = screen_width - self.pixels_from_right
        self.curr_height = screen_height - self.pixels_from_bottom
        self.root.geometry('%dx%d+%d+%d' % (100, 100, self.curr_width, self.curr_height))
        
        # 创建右键菜单
        self.create_context_menu()

    def update(self, i, curr_animation):
        # print("Curently: %s" % curr_animation)
        self.current_animation = curr_animation  # 更新当前动画状态
        self.root.attributes('-topmost', True)  # put window on top
        animation_arr = self.animation[curr_animation]
        frame = animation_arr[i]
        self.label.configure(image=frame)

        # move the pet if needed
        if curr_animation in ('walk_left', 'walk_right'):
            self.move_window(curr_animation)

        i += 1
        if i == len(animation_arr):
            # reached end of this animation, decide on the next animation
            next_animation = self.getNextAnimation(curr_animation)
            # 取消之前的任务
            if self.after_id:
                self.root.after_cancel(self.after_id)
            # 启动新的任务并保存ID
            self.after_id = self.root.after(self.delay, self.update, 0, next_animation)
        else:
            # 取消之前的任务
            if self.after_id:
                self.root.after_cancel(self.after_id)
            # 启动新的任务并保存ID
            self.after_id = self.root.after(self.delay, self.update, i, curr_animation)

    def onLeftClick(self, event):
        print("detected left click")
        # 点击交互，切换到随机状态
        if self.current_animation != 'sleep':
            # 取消之前的任务
            if self.after_id:
                self.root.after_cancel(self.after_id)
            # 设置新的动画状态
            self.current_animation = random.choice(['idle', 'walk_left', 'walk_right'])
            # 启动新的动画更新任务
            self.after_id = self.root.after(self.delay, self.update, 0, self.current_animation)

    def on_enter(self, event):
        """鼠标进入时的处理"""
        if self.current_animation in ('walk_left', 'walk_right'):
            self.previous_animation = self.current_animation
            # 取消之前的任务
            if self.after_id:
                self.root.after_cancel(self.after_id)
            # 设置新的动画状态
            self.current_animation = 'idle'
            # 启动新的动画更新任务
            self.after_id = self.root.after(self.delay, self.update, 0, 'idle')

    def on_leave(self, event):
        """鼠标离开时的处理"""
        if hasattr(self, "previous_animation") and self.previous_animation in ('walk_left', 'walk_right') and self.current_animation == 'idle':
            # 取消之前的任务
            if self.after_id:
                self.root.after_cancel(self.after_id)
            # 设置新的动画状态
            self.current_animation = self.previous_animation
            # 启动新的动画更新任务
            self.after_id = self.root.after(self.delay, self.update, 0, self.previous_animation)
            delattr(self, "previous_animation")

    def start_drag(self, event):
        """开始拖拽"""
        if self.current_animation != 'sleep':
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag(self, event):
        """拖拽中"""
        if self.current_animation != 'sleep':
            x = self.root.winfo_x() + (event.x - self.drag_data["x"])
            y = self.root.winfo_y() + (event.y - self.drag_data["y"])
            # 限制拖拽范围
            x = max(self.min_width, min(self.max_width, x))
            y = max(self.min_height, min(self.max_height, y))
            self.root.geometry(f"+{x}+{y}")
            self.curr_width, self.curr_height = x, y  # 更新位置记录

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tkinter.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Idle 状态", command=lambda: self.set_animation('idle'))
        self.context_menu.add_command(label="Walk 状态", command=lambda: self.set_animation(random.choice(['walk_left', 'walk_right'])))
        self.context_menu.add_command(label="Sleep 状态", command=lambda: self.set_animation('sleep'))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="退出", command=self.quit)

    def show_context_menu(self, event):
        """显示右键菜单"""
        self.context_menu.post(event.x_root, event.y_root)

    def set_animation(self, animation):
        """设置动画状态"""
        # 取消之前的任务
        if self.after_id:
            self.root.after_cancel(self.after_id)
        # 设置新的动画状态
        self.current_animation = animation
        # 启动新的动画更新任务
        self.after_id = self.root.after(self.delay, self.update, 0, animation)

    def move_window(self, curr_animation):
        if curr_animation == 'walk_left':
            if self.curr_width > self.min_width:
                self.curr_width -= self.move_speed
            else:
                # 碰到左边缘，切换到向右走
                self.current_animation = 'walk_right'
                self.root.after(self.delay, self.update, 0, 'walk_right')

        elif curr_animation == 'walk_right':
            if self.curr_width < self.max_width:
                self.curr_width += self.move_speed
            else:
                # 碰到右边缘，切换到向左走
                self.current_animation = 'walk_left'
                self.root.after(self.delay, self.update, 0, 'walk_left')

        self.root.geometry('%dx%d+%d+%d' % (100, 100, self.curr_width, self.curr_height))

    def getNextAnimation(self, curr_animation):
        # 保持当前状态，不自动切换
        return curr_animation

    def run(self):
        # 启动动画更新任务并保存ID
        self.after_id = self.root.after(self.delay, self.update, 0, 'idle')  # start on idle
        self.root.mainloop()

    def quit(self):
        self.root.destroy()


if __name__ == '__main__':
    print('Initializing your desktop pet...')
    print('To quit, right click on the pet')
    pet = Pet()
    pet.run()