# from transformers import pipeline  # Ensure transformers library is installed via pip
#
# # Инициализируем модель и токенизатор
# generator = pipeline(
#     "text-generation",
#     model="ai-forever/rugpt3small_based_on_gpt2",
#     tokenizer="ai-forever/rugpt3small_based_on_gpt2",
#     framework="pt",  # Явно указываем, что используется PyTorch
# )
#
# def get_chatbot_response(prompt):
#     try:
#         # Генерируем текст
#         response = generator(
#             prompt,
#             max_length=50,  # Длина ответа
#             num_return_sequences=1,  # Количество вариантов
#             pad_token_id=generator.tokenizer.eos_token_id,  # Убираем ошибки с отсутствием <pad>
#         )
#         return response[0]["generated_text"]  # Возвращаем текст ответа
#     except Exception as e:
#         return f"Ошибка: {e}"
