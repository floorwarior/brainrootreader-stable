

def get_next_port(starting_port,interval):
    def helper():
        f = starting_port
        while True:
            yield f
            f += (interval)
    return helper()

if __name__ == "__main__":
    f = get_next_port(4222,4)
    for i in range(10):
        print(next(f))
