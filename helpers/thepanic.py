import logging
import traceback
import time

class PanTheGuyofPanics():


    def __init__(pan,logfiles_name):
        pan.logger = logging.getLogger(logfiles_name)
        pan.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logfiles_name)
        pan.logger.addHandler(handler)
        pan.attached = {}


    def register_handler(pan,name_of_func,func):
        """if you are using a modul scoped function as handler, you need to register it otherwise it will not be found,
            example
            ```
            # in the submodul somemodul

            def example_handler(*args,**kwargs):
                print(kwargs.get("error"))

            pan.register_handler('example_handler',example_handler)


            ### then later
            class Dummy():
            
                def __init__(self,name):
                    self.name =  name

                @staticmethod
                @pan.panic(on_panic="example_handler",class_method=False)
                def raise_example_Error(self): 
                    raise BaseException("this is an example")
            ```

            if you would to import the class, and the event \n was not registered, panic would not find
            your handler, even if it was imported alongside the class, thats why we need to register it
        """
        pan.attached[name_of_func] = func

    def try_until(pan,timeout,maxtries,default_value=None):
        """tries to execute a function until it works, or it hits maximum tries, should be used with network bound tasks"""
        def decorator(func):
            def wrapper(*args,**kwargs):
                success = False
                tries = 0
                error = None
                while not success and tries < maxtries:
                    try:
                        return func(*args,**kwargs)
                    except Exception as e:
                        error = e
                        tries += 1
                        traceback.print_exc()
                        print(f"{tries} / {maxtries} ")

                        time.sleep(timeout)
                if not success and not default_value:
                    print(f"we caught this error for you:", error)
                    print("these values were passed:")
                    for i,a in enumerate(args):
                        print(f"i:{i}", a)
                    for key,val in kwargs.items():
                        print(f"key: {key}, value: {val}")
                    pan.logger.info(error)
                    raise BaseException("maximum tries reached with try_until")
                else:
                    return default_value
            return wrapper
        return decorator

    def panic(pan,on_panic,class_method=False):
        def decorator(func):
            def wrapper(*args,**kwargs):
                try:
                    return func(*args,**kwargs)
                except Exception as e:
                    traceback.print_exc()
                    print(f"""**Thank you for chosing Panic** you choose this function to handle the panic: {on_panic}""")
                    print(f"we caught this error for you:", e)
                    print("these values were passed:")
                    for i,a in enumerate(args):
                        print(f"i:{i}", a)
                    for key,val in kwargs.items():
                        print(f"key: {key}, value: {val}")

                    
                    pan.logger.info(e)
                    if class_method:
                        return args[0].__getattribute__(on_panic)(*args,error=e,**kwargs)
                    else:
                        if on_panic in globals():
                            panic_handler = globals()[on_panic]
                        elif on_panic in pan.attached:
                            return pan.attached[on_panic](*args,error=e,**kwargs)
                        else:
                            import builtins
                            panic_handler = getattr(builtins,on_panic)
                        return panic_handler(*args,error=e,**kwargs)
            return wrapper
        return decorator

Pan = PanTheGuyofPanics("bookreaderpannics.log")

