class Generic:
    class Text:
        class Large:
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                return None
