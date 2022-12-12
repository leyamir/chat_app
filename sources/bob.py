import ui
import App
import threading

lock = threading.Lock()
my_ip = 'localhost'
my_port = 8081
my_name = "Bob"
bg_job = App.Peer(my_ip, my_port, my_name, lock=lock)
bg_job.connect_to_server(('localhost', 8070))
bg_job.start()
app = ui.MainUi(background_job=bg_job, title_name=my_name)
app.title = my_name
app.after(500, app.show_mesage)
app.mainloop()
bg_job.terminate = True
bg_job.server_interact("exit")