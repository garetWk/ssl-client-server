from tkinter import *
from tkinter.messagebox import *
import time, _thread as thread 
from socket import *
import ssl
import pprint


myHost = '127.0.0.1'
myPort = 50007


sockObj = socket(AF_INET, SOCK_STREAM)

try:
    ssl_sock = ssl.wrap_socket(sockObj,
                               certfile="clientcert.pem",
                               keyfile="clientcert.pem",
                               ca_certs="servercert.pem",
                               cert_reqs=ssl.CERT_REQUIRED)
    ssl_sock.connect((myHost,myPort))
except Exception as e:
    showinfo("Error", "SSL Handshaking failed!")
    log = open("log.txt", 'a')
    log.write(str(e))
    log.write('\n')
    log.close()
    raise e


print (repr(ssl_sock.getpeername()))
print (ssl_sock.cipher())
print (pprint.pformat(ssl_sock.getpeercert()))
print('client is connected')


class logInDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        self.focus_set()
        
        self.title('log in')
        
        Label(self,text='id').grid(row=0)
        ent1 = self.id = Entry(self)
        ent1.grid(row=0 , column=1)

        Label(self,text='password').grid(row=1)
        ent2 = self.password = Entry(self)
        ent2.grid(row=1, column=1)

        Button(self, text='Enter', command=self.verify).grid(row=2 , column=0, sticky=W)
        Button(self, text='Close', command=self.close).grid(row=2 , column=1, sticky=E)

        self.bind("<Return>", self.verify)
        self.bind("<Escape>" , self.close)
        
        self.parent = parent
        
        self.grab_set()
        self.wait_window(self)
        

    def close(self, event=None):
        if askyesno('Verify', 'Do you really want to close?'):
            self.grab_release()
            self.parent.focus_set()
            self.destroy()

    def verify(self, event=None):
        command = 'verify'
        ssl_sock.send(command.encode())
        
        msg = self.id.get() + " " + self.password.get()
        ssl_sock.send(msg.encode())
        
        response = ssl_sock.recv(1024).decode()

        print(response)
        
        if response == 'valid' :
            if showinfo("Info", "log in successfully!"):
                makemenu(root,True)
                self.grab_release()
                self.parent.focus_set()
                self.destroy()
                
        elif response == 'invalid' :
            showinfo("Info", "log in unsuccessfully!")
            
        else:
            print("Error invalid respose was sent!")
        
class measurementDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        self.focus_set()
        
        self.title('measurements')
        
        Label(self,text='Height').grid(row=0)
        ent1 = self.height = Entry(self)
        ent1.grid(row=0 , column=1)

        Label(self,text='Weight').grid(row=1)
        ent2 = self.weight = Entry(self)
        ent2.grid(row=1, column=1)

        Label(self,text='BP').grid(row=2)
        ent2 = self.bp = Entry(self)
        ent2.grid(row=2, column=1)

        Button(self, text='Enter', command=self.store).grid(row=3 , column=0, sticky=W)
        Button(self, text='Close', command=self.close).grid(row=3 , column=1, sticky=E)

        self.bind("<Return>", self.store)
        self.bind("<Escape>" , self.close)
        
        self.parent = parent
        
        self.grab_set()
        self.wait_window(self)
        

    def close(self, event=None):
        if askyesno('Verify', 'Do you really want to close?'):
            self.grab_release()
            self.parent.focus_set()
            self.destroy()

    def store(self, event=None):
        command = 'measurement storage'
        ssl_sock.send(command.encode())
        
        msg = (self.height.get() + ' ' + self.weight.get() + ' ' + self.bp.get())
        ssl_sock.send(msg.encode())

        response = ssl_sock.recv(1024).decode()

        print(response)

        self.grab_release()
        self.parent.focus_set()
        self.destroy()



def login():   
    d = logInDialog(root)

def current():
    m = measurementDialog(root)


def last():
    command = 'measurement retrieve'
    ssl_sock.send(command.encode())
    response = ssl_sock.recv(1024).decode()
    showinfo("Last Measurement Info", response)

def save():
    if askokcancel("Save", "This will end the connection and exit the program. Save?"):
        ssl_sock.shutdown(SHUT_RDWR)
        print('connection read/write shutdown')
        ssl_sock.close()
        print('connection closed')
        root.destroy()
        
def logout():
    if askyesno('Lout out', 'This will end the connection to the server. Log out?'):
        ssl_sock.shutdown(SHUT_RDWR)
        print('connection read/write shutdown')
        ssl_sock.close()
        print('connection closed')
        makemenu(root, False)

def makemenu(win,cond):
    top = Menu(win)
    win.config(menu=top)
    
    file = Menu(top)
    top.add_cascade(label='File', menu=file, underline=0) 
    account = Menu(top)
    top.add_cascade(label='Account', menu=account, underline=0) 
    measure = Menu(top)
    top.add_cascade(label='Measure', menu=measure, underline=0)
    
    if cond==False:        
        file.add_command(label='Save', command=save, underline=0,state='disabled')        
        account.add_command(label='Log-In', command=login, underline=0,state='active')
        account.add_command(label='Log-Out', command=logout, underline=0,state='disabled')
        measure.add_command(label='Current', command=current, underline=0, state='disabled')
        measure.add_command(label='Last', command=last, underline=0, state='disabled')
    else:
        file.add_command(label='Save', command=save, underline=0,state='active')        
        account.add_command(label='Log-In', command=login, underline=0,state='disabled')
        account.add_command(label='Log-Out', command=logout, underline=0,state='active')
        measure.add_command(label='Current', command=current, underline=0, state='active')
        measure.add_command(label='Last', command=last, underline=0, state='active')


if __name__ == '__main__':
    root = Tk()
    root.geometry('200x200')
    makemenu(root,False)
    root.title('ECE424 Lab2 Client')


    root.mainloop()
