"""Single-container web + durable worker; exit together on child failure or SIGTERM."""
import os,signal,subprocess,sys,time

def main():
    children=[];stopping=False
    def stop(*args):
        nonlocal stopping
        stopping=True
        for child in children:
            if child.poll() is None:child.terminate()
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    port=os.environ.get('PORT','10000')
    if not port.isdigit():raise SystemExit('PORT must be numeric')
    children.append(subprocess.Popen([sys.executable,'manage.py','run_platform_worker']))
    children.append(subprocess.Popen(['gunicorn','config.wsgi:application','--bind','0.0.0.0:'+port,'--workers','2','--timeout','60','--access-logfile','-','--error-logfile','-']))
    code=0
    try:
        while not stopping:
            for child in children:
                result=child.poll()
                if result is not None:code=result or 1;stop();break
            if not stopping:time.sleep(.25)
    finally:
        stop()
        for child in children:
            try:child.wait(timeout=20)
            except subprocess.TimeoutExpired:child.kill();child.wait()
    return code

if __name__=='__main__':raise SystemExit(main())
