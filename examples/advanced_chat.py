"""
Advanced chat examples for LokisApi Python library.
Demonstrates Thinking (Gemini 2.5) and Reasoning Effort (GPT-5) features.
"""

from lokisapi import (
    LokisApiClient, ChatMessage, ChatRole, ChatCompletionRequest,
    ReasoningEffort, THINKING_MODELS, estimate_tokens
)


def main():
    # Initialize the client
    client = LokisApiClient("YOUR_API_KEY")
    
    print("=== LokisApi Advanced Chat Examples ===\n")
    
    # Example 1: Thinking mode with Gemini 2.5 Pro
    print("1. Thinking Mode with Gemini 2.5 Pro:")
    try:
        messages = [
            ChatMessage(ChatRole.USER, """
            Реши эту сложную математическую задачу пошагово:
            
            У нас есть прямоугольник со сторонами 12 см и 8 см. 
            Внутри него нарисован круг, касающийся всех четырех сторон.
            Найдите площадь части прямоугольника, которая находится вне круга.
            """)
        ]
        
        response = client.chat(
            messages=messages,
            model="gemini-2.5-pro",
            thinking=True,
            thinking_budget=3000,
            temperature=0.3
        )
        
        print(f"   Response: {response.choices[0]['message']['content']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 2: Different thinking budgets
    print("2. Different Thinking Budgets:")
    try:
        problem = "Объясни принцип работы квантовых компьютеров и их преимущества"
        
        budgets = [500, 1500, 3000]
        
        for budget in budgets:
            print(f"   Testing with thinking budget: {budget}")
            messages = [ChatMessage(ChatRole.USER, problem)]
            
            response = client.chat(
                messages=messages,
                model="gemini-2.5-flash",
                thinking=True,
                thinking_budget=budget,
                temperature=0.5
            )
            
            content = response.choices[0]['message']['content']
            tokens = estimate_tokens(content)
            print(f"   Budget {budget}: {tokens} tokens, {len(content)} characters")
            print(f"   Preview: {content[:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 3: Reasoning Effort with GPT-5
    print("3. Reasoning Effort with GPT-5:")
    try:
        reasoning_levels = [
            (ReasoningEffort.MINIMAL, "minimal"),
            (ReasoningEffort.MEDIUM, "medium"),
            (ReasoningEffort.HIGH, "high")
        ]
        
        problem = "Проанализируй экономические последствия перехода на возобновляемые источники энергии"
        
        for effort, level_name in reasoning_levels:
            print(f"   Testing with reasoning effort: {level_name}")
            messages = [ChatMessage(ChatRole.USER, problem)]
            
            response = client.chat(
                messages=messages,
                model="gpt-5",
                reasoning_effort=effort,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0]['message']['content']
            tokens = estimate_tokens(content)
            print(f"   {level_name.capitalize()} effort: {tokens} tokens")
            print(f"   Preview: {content[:150]}...")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 4: Streaming with Thinking
    print("4. Streaming with Thinking:")
    try:
        messages = [
            ChatMessage(ChatRole.SYSTEM, "Ты - эксперт по программированию. Объясняй сложные концепции простыми словами."),
            ChatMessage(ChatRole.USER, "Объясни принцип работы рекурсии в программировании с примерами")
        ]
        
        print("   Streaming response with thinking:")
        full_response = ""
        
        for chunk in client.chat(
            messages=messages,
            model="gemini-2.5-flash",
            thinking=True,
            thinking_budget=2000,
            stream=True
        ):
            if chunk.choices[0].get('delta', {}).get('content'):
                content = chunk.choices[0]['delta']['content']
                full_response += content
                print(content, end='', flush=True)
        
        print(f"\n   ✅ Complete response received ({len(full_response)} characters)")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 5: Complex problem solving with Thinking
    print("5. Complex Problem Solving with Thinking:")
    try:
        complex_problem = """
        Задача: Компания планирует открыть новый филиал в городе с населением 500,000 человек.
        
        Известно:
        - Средний доход на душу населения: $45,000/год
        - Конкуренты: 3 крупные компании, 15 средних, 50 малых
        - Аренда офиса: $25/кв.м/месяц
        - Средняя зарплата сотрудника: $60,000/год
        - Налоги: 25% от прибыли
        
        Вопросы:
        1. Какой размер офиса выбрать (от 100 до 1000 кв.м)?
        2. Сколько сотрудников нанять (от 5 до 50)?
        3. Какую ценовую стратегию использовать?
        4. Какие риски учесть?
        
        Предоставь детальный анализ с расчетами.
        """
        
        messages = [ChatMessage(ChatRole.USER, complex_problem)]
        
        response = client.chat(
            messages=messages,
            model="gemini-2.5-pro",
            thinking=True,
            thinking_budget=5000,
            temperature=0.2,
            max_tokens=4000
        )
        
        content = response.choices[0]['message']['content']
        print(f"   Complex analysis completed:")
        print(f"   Response length: {len(content)} characters")
        print(f"   Estimated tokens: {estimate_tokens(content)}")
        print(f"   Preview: {content[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 6: Model comparison
    print("6. Model Comparison (Thinking vs Non-Thinking):")
    try:
        question = "Как работает машинное обучение? Объясни алгоритм обучения нейронной сети."
        
        # With thinking
        print("   With Thinking (Gemini 2.5 Pro):")
        messages = [ChatMessage(ChatRole.USER, question)]
        
        response_thinking = client.chat(
            messages=messages,
            model="gemini-2.5-pro",
            thinking=True,
            thinking_budget=2000
        )
        
        content_thinking = response_thinking.choices[0]['message']['content']
        tokens_thinking = estimate_tokens(content_thinking)
        
        print(f"   Thinking model: {tokens_thinking} tokens")
        print(f"   Preview: {content_thinking[:150]}...")
        
        # Without thinking
        print("\n   Without Thinking (Gemini 2.0 Flash):")
        response_normal = client.chat(
            messages=messages,
            model="gemini-2.0-flash",
            thinking=False
        )
        
        content_normal = response_normal.choices[0]['message']['content']
        tokens_normal = estimate_tokens(content_normal)
        
        print(f"   Normal model: {tokens_normal} tokens")
        print(f"   Preview: {content_normal[:150]}...")
        
        print(f"\n   Comparison: Thinking model used {tokens_thinking - tokens_normal} more tokens")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 7: Available models with Thinking support
    print("7. Models Supporting Thinking:")
    try:
        print(f"   Models with Thinking support: {THINKING_MODELS}")
        
        for model_id in THINKING_MODELS:
            print(f"   - {model_id}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    main()
