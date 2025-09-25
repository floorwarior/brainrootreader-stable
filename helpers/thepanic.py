import logging
import traceback
class PanTheGuyofPanics():


    def __init__(pan,logfiles_name):
        pan.logger = logging.getLogger(logfiles_name)
        pan.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logfiles_name)
        pan.logger.addHandler(handler)

    def panic(pan,on_panic,class_method=False):
        def decorator(func):
            def wrapper(*args,**kwargs):
                try:
                    if class_method:
                        return func(*args,**kwargs)
                    else:
                        return func(*args,**kwargs)
                except Exception as e:
                    print(f"""**Thank you for chosing Panic** you choose this function to handle the panic: {on_panic}""")
                    print(f"we caught this error for you:", e)
                    traceback.print_exc()
                    pan.logger.info(e)
                    if class_method:
                        return args[0].__getattribute__(on_panic)(error=e)
                    else:
                        if on_panic in globals():
                            panic_handler = globals()[on_panic]
                        else:
                            import builtins
                            panic_handler = getattr(builtins,on_panic)
                        return panic_handler(*args,error=e,**kwargs)
            return wrapper
        return decorator

Pan = PanTheGuyofPanics("bookreaderpannics.log")

