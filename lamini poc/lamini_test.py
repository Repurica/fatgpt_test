from llama import LLMEngine, Type, Context

class Test(Type):
    test_string: str = Context("just a test")

llm = LLMEngine(
    id="example_llm",
    config={"production.key": "341b5e3c08273b56ffc8b71a1ff9877f8753646d"}
    )
test = Test(test_string="testing 123")
llm(test, output_type=Test)
print(test, test.test_string)

print('test')