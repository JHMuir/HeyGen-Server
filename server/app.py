from fastapi import FastAPI


class FastAPIApp:
    def __init__(self):
        self.app = FastAPI(title="Video Translation Server")
