class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose:
                print(stack, '<---||--->', w[cursor:])

            # Your code here!!! (Detect error)
            if not self.action[state, lookahead]:
                raise Exception("No transition available")

            action, tag = self.action[state, lookahead]
            # Your code here!!! (Shift case)
            # Your code here!!! (Reduce case)
            # Your code here!!! (OK case)
            # Your code here!!! (Invalid case)
            if action == self.SHIFT:
                stack.append(tag)
                cursor += 1
            elif action == self.REDUCE:
                stack = stack[:len(stack) - len(tag.Right)]
                goto = self.goto[stack[-1], tag.Left]
                stack.append(goto)
                output.append(tag)
            elif action == self.OK:
                print('OK')
                return output
            else:
                raise Exception('Invalid case')
                return
