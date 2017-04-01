from idemseq.sequence import SequenceBase

seq = SequenceBase()


@seq.command(rerun_always=True)
def greeting():
    print('Hello!')


@seq.command(rerun_until_all_finished=True)
def ensure_server_is_running(server=None):
    assert server is not None


@seq.command
def install_packages(server):
    server.append('package1')
    server.append('package2')


@seq.command
def ensure_server_is_shut_down(server):
    print(server)


server = []


installer = seq('/tmp/xyz.db')
installer.reset()

while not installer.is_finished:
    installer.run(context=dict(server=server))
