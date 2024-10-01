#2 threads - potential problems with managing current situation especially when we are attacked.
# code with aim to threading in future, but without real need better not to complicate

#1 - regulary get picture and return in [['#FFDDCC', '#FFDDAA'],] format
#2 - 
#    - load tasks from task folder
#    - ask current state of picture 
#    - draw pixels (input: task, account and return coords of completed pixels)
#        - login telegram webapp during drawing (it will also auto update akk)
#        - ...
from PIL import Image
import code

from notpixel_actions import PixelActions
from notpixel_tools import *


class Worker:
    def __init__(self, tg_acc_name):
        self.tg_acc_name = tg_acc_name

class Fucktory:
    def __init__(self, picture_path, location):
        self.img = Image.open(picture_path).convert('RGB')
        self.pixels = self.img.load()
        assert len(location) == 2 # x, y
        assert type(location[0]) == int
        assert type(location[1]) == int
        self.location = location
        print(f'Initialized Fucktory size of {self.img.size}')
        #code.interact(local=locals())
    
    def get_job(self):
        return get_job(self.img, self.location)
    
    def get_workers(self, accs):
        self.workers = [Worker(acc) for acc in accs]

    def split_task_by_workers(self, task):
        pass

    
        

if __name__ == '__main__':
    picture_path = './notpixel_settings/228.png'
    fk = Fucktory(picture_path, (228, 228))
    task = fk.get_job()
    code.interact(local=locals())
    # some logic on how much workers needed for task
    fk.get_workers(['wc1', 'wc2', 'wc3'])
    # some logic on parallel/non parallel run of the job
    fk.split_task_by_workers(task)