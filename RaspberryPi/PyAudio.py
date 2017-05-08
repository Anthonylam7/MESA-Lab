from subprocess import Popen, PIPE
from os import listdir, getcwd
from queue import Queue



class Audio(object):
    def __init__(self):
        try:
            self.file_list = listdir(getcwd()+'/Audio/')
            print('success')
        except Exception as e:
            print(e)
            self.file_list = listdir()
        self.audio_list = ['{}/Audio/{}'.format(getcwd(),filename) for filename in self.file_list]
        self.process = None
        self.queue = Queue()


    def play(self, filepath):
        if self.process is None:
            print('Playing', filepath)
            self.process = Popen(['omxplayer', filepath], stdin=PIPE)
        else:
            print('queued',filepath)
            self.queue.put(filepath)

    def play_queue(self):
        if self.process.poll() is not None:
            self.process = None

        if self.process is None:
            file =  self.queue.get()
            print('Playing: ', file)
            self.process = Popen(['omxplayer',file], stdin=PIPE)






    def stop(self):
        if self.process is not None:
            p = self.process
            try:
                p.stdin.write('q')
                p.terminate()
                p.wait()  # -> move into background thread if necessary
            except EnvironmentError as e:
                logger.error("can't stop %s: %s", self.file_list, e)
            else:
                self.process = None


if __name__ == '__main__':
    a = Audio()

    for audio in a.audio_list:
        a.play(audio)
    print(a.queue)
    while(a.queue.empty() is not None):
        a.play_queue()