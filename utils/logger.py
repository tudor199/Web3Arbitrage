class Logger:
    def __init__(self, fileDescriptor, level=0, nextLogger=None):
        self.fd = fileDescriptor
        self.level = level
        self.nextLogger = nextLogger

    def write(self, message: str, level: int):
        if self.level <= level:
            self.fd.write(f"{message}\n")
            self.fd.flush()
        if self.nextLogger:
            self.nextLogger.write(message, level)

    def close(self):
        self.fd.close()
        if self.nextLogger:
            self.nextLogger.close()
