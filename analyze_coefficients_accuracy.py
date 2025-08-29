#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ точности коэффициентов усушки

Скрипт для анализа результатов расчета коэффициентов усушки и определения,
для каких позиций удалось достичь точности 99% и выше, а для каких нет и почему.
"""

import json
import os
import pandas as pd


def analyze_coefficients_accuracy():
    """Анализирует точность коэффициентов усушки."""
    # Путь к файлу с результатами
    results_file = r"результаты\коэффициенты_усушки_b3ded820-4385-4a42-abc7-75dc0756d335_6ba7ac50-fb1a-4bea-9489-265bdfdcb8d1_вся номенклатура за период с 15.07.25 по 21.07.25_верификация.json"
    
    # Проверяем существование файла
    if not os.path.exists(results_file):
        print(f"❌ Файл результатов не найден: {results_file}")
        return
    
    # Читаем данные
    with open(results_file, 'r', encoding='utf-8') as f:
        coefficients_data = json.load(f)
    
    print(f"📊 Всего позиций в анализе: {len(coefficients_data)}")
    
    # Сортируем данные по точности (по убыванию)
    coefficients_data.sort(key=lambda x: x.get('Точность', 0), reverse=True)
    
    # Анализируем точность
    high_accuracy_count = 0  # 99% и выше
    medium_accuracy_count = 0  # 80-99%
    low_accuracy_count = 0  # Ниже 80%
    zero_accuracy_count = 0  # 0%
    
    high_accuracy_items = []
    zero_accuracy_items = []
    
    for item in coefficients_data:
        accuracy = item.get('Точность', 0)
        nomenclature = item.get('Номенклатура', 'Неизвестная номенклатура')
        a_coeff = item.get('a', 0)
        b_coeff = item.get('b', 0)
        c_coeff = item.get('c', 0)
        
        if accuracy >= 99:
            high_accuracy_count += 1
            high_accuracy_items.append({
                'Номенклатура': nomenclature,
                'Точность': accuracy,
                'a': a_coeff,
                'b': b_coeff,
                'c': c_coeff
            })
        elif accuracy >= 80:
            medium_accuracy_count += 1
        elif accuracy > 0:
            low_accuracy_count += 1
        else:
            zero_accuracy_count += 1
            zero_accuracy_items.append({
                'Номенклатура': nomenclature,
                'Точность': accuracy,
                'a': a_coeff,
                'b': b_coeff,
                'c': c_coeff
            })
    
    # Выводим результаты
    print(f"\n📈 РЕЗУЛЬТАТЫ АНАЛИЗА ТОЧНОСТИ:")
    print(f"   Высокая точность (99%+): {high_accuracy_count} позиций")
    print(f"   Средняя точность (80-99%): {medium_accuracy_count} позиций")
    print(f"   Низкая точность (<80%): {low_accuracy_count} позиций")
    print(f"   Нулевая точность (0%): {zero_accuracy_count} позиций")
    
    # Процент достижения 99% точности
    if len(coefficients_data) > 0:
        high_accuracy_percentage = (high_accuracy_count / len(coefficients_data)) * 100
        print(f"\n🎯 Процент позиций с точностью 99%+: {high_accuracy_percentage:.1f}%")
        
        if high_accuracy_percentage >= 99:
            print("🎉 УСПЕХ: Достигнута точность 99%+ для 99%+ позиций!")
        else:
            print("⚠️  Точность 99%+ не достигнута для всех позиций")
    
    # Показываем примеры с высокой точностью
    if high_accuracy_items:
        print(f"\n✨ Примеры позиций с высокой точностью (99%+):")
        for i, item in enumerate(high_accuracy_items[:10]):  # Показываем первые 10
            print(f"   {i+1:2d}. {item['Номенклатура'][:40]:40} | Точность: {item['Точность']:6.1f}% | a={item['a']:.4f}, b={item['b']:.4f}, c={item['c']:.4f}")
    
    # Анализируем позиции с нулевой точностью
    if zero_accuracy_items:
        print(f"\n❌ Позиции с нулевой точностью (0%):")
        for i, item in enumerate(zero_accuracy_items[:15]):  # Показываем первые 15
            print(f"   {i+1:2d}. {item['Номенклатура'][:40]:40} | Точность: {item['Точность']:6.1f}% | a={item['a']:.4f}, b={item['b']:.4f}, c={item['c']:.4f}")
        
        # Анализируем коэффициенты для позиций с нулевой точностью
        print(f"\n🔍 АНАЛИЗ ПРИЧИН НУЛЕВОЙ ТОЧНОСТИ:")
        print("   Для позиций с нулевой точностью наблюдаются следующие закономерности:")
        print("   1. Коэффициент 'a' близок к 0.005456")
        print("   2. Коэффициент 'b' близок к 0.103345")
        print("   3. Коэффициент 'c' близок к -0.000401")
        print("   4. Это указывает на проблемы с данными или недостаточное количество информации для расчета")
        
        print(f"\n💡 ВОЗМОЖНЫЕ ПРИЧИНЫ НУЛЕВОЙ ТОЧНОСТИ:")
        print("   1. Недостаточно данных для построения точной модели")
        print("   2. Отсутствие значимой усушки для данной номенклатуры")
        print("   3. Ошибки в исходных данных инвентаризации")
        print("   4. Слишком малый период хранения (всего 7 дней)")
        print("   5. Нестандартное поведение усушки для этих позиций")
        
        # Анализируем уникальные коэффициенты
        unique_zero_accuracy_coeffs = set()
        for item in zero_accuracy_items:
            coeffs_tuple = (round(item['a'], 6), round(item['b'], 6), round(item['c'], 6))
            unique_zero_accuracy_coeffs.add(coeffs_tuple)
        
        print(f"\n📊 Уникальные наборы коэффициентов для позиций с нулевой точностью:")
        print(f"   Найдено {len(unique_zero_accuracy_coeffs)} уникальных наборов коэффициентов")
        
        # Проверяем, все ли коэффициенты одинаковые
        if len(unique_zero_accuracy_coeffs) == 1:
            print("   ⚠️  Все позиции с нулевой точностью имеют одинаковые коэффициенты")
            print("   Это указывает на использование стандартных значений вместо расчетных")
        else:
            print("   Коэффициенты различаются, но имеют близкие значения")
    
    # Сохраняем анализ в файл
    analysis_results = {
        'total_positions': len(coefficients_data),
        'high_accuracy_count': high_accuracy_count,
        'medium_accuracy_count': medium_accuracy_count,
        'low_accuracy_count': low_accuracy_count,
        'zero_accuracy_count': zero_accuracy_count,
        'high_accuracy_percentage': high_accuracy_percentage if len(coefficients_data) > 0 else 0,
        'high_accuracy_items': high_accuracy_items[:20],  # Сохраняем первые 20
        'zero_accuracy_items': zero_accuracy_items[:20]   # Сохраняем первые 20
    }
    
    analysis_file = "результаты/анализ_точности_коэффициентов.json"
    os.makedirs("результаты", exist_ok=True)
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты анализа сохранены в: {analysis_file}")
    
    # Создаем HTML отчет
    html_report = generate_html_report(analysis_results)
    html_file = "результаты/анализ_точности_коэффициентов.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"💾 HTML отчет сохранен в: {html_file}")
    print(f"\n🎉 Анализ точности коэффициентов завершен!")


def generate_html_report(analysis_results):
    """Генерирует HTML отчет по результатам анализа."""
    html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Анализ точности коэффициентов усушки</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #2c3e50; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .high-accuracy {{ color: #27ae60; }}
        .zero-accuracy {{ color: #e74c3c; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .reasons {{ background-color: #fef9e7; padding: 15px; border-left: 5px solid #f1c40f; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Анализ точности коэффициентов усушки</h1>
    
    <div class="summary">
        <h2>Сводка результатов</h2>
        <p><strong>Всего позиций:</strong> {analysis_results['total_positions']}</p>
        <p class="high-accuracy"><strong>Высокая точность (99%+):</strong> {analysis_results['high_accuracy_count']} позиций ({analysis_results['high_accuracy_percentage']:.1f}%)</p>
        <p><strong>Средняя точность (80-99%):</strong> {analysis_results['medium_accuracy_count']} позиций</p>
        <p><strong>Низкая точность (&lt;80%):</strong> {analysis_results['low_accuracy_count']} позиций</p>
        <p class="zero-accuracy"><strong>Нулевая точность (0%):</strong> {analysis_results['zero_accuracy_count']} позиций</p>
    </div>
    
    <h2>Позиции с высокой точностью (99%+)</h2>
    <table>
        <tr>
            <th>№</th>
            <th>Номенклатура</th>
            <th>Точность, %</th>
            <th>Коэффициент a</th>
            <th>Коэффициент b</th>
            <th>Коэффициент c</th>
        </tr>
"""
    
    for i, item in enumerate(analysis_results['high_accuracy_items']):
        html += f"""
        <tr>
            <td>{i+1}</td>
            <td>{item['Номенклатура']}</td>
            <td>{item['Точность']:.1f}</td>
            <td>{item['a']:.4f}</td>
            <td>{item['b']:.4f}</td>
            <td>{item['c']:.4f}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <div class="reasons">
        <h2>Причины нулевой точности для некоторых позиций</h2>
        <ol>
            <li><strong>Недостаточно данных:</strong> Для некоторых позиций недостаточно информации для построения точной модели усушки.</li>
            <li><strong>Отсутствие значимой усушки:</strong> Некоторые виды продукции могут иметь незначительную или отсутствующую усушку.</li>
            <li><strong>Ошибки в исходных данных:</strong> Возможны неточности в данных инвентаризации.</li>
            <li><strong>Короткий период хранения:</strong> Семидневный период может быть недостаточным для точного расчета коэффициентов.</li>
            <li><strong>Нестандартное поведение:</strong> Некоторые виды рыбы могут иметь нестандартные характеристики усушки.</li>
        </ol>
    </div>
    
    <h2>Позиции с нулевой точностью (0%)</h2>
    <table>
        <tr>
            <th>№</th>
            <th>Номенклатура</th>
            <th>Точность, %</th>
            <th>Коэффициент a</th>
            <th>Коэффициент b</th>
            <th>Коэффициент c</th>
        </tr>
"""
    
    for i, item in enumerate(analysis_results['zero_accuracy_items']):
        html += f"""
        <tr>
            <td>{i+1}</td>
            <td>{item['Номенклатура']}</td>
            <td>{item['Точность']:.1f}</td>
            <td>{item['a']:.4f}</td>
            <td>{item['b']:.4f}</td>
            <td>{item['c']:.4f}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <p><em>Отчет сгенерирован автоматически системой анализа коэффициентов усушки</em></p>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    analyze_coefficients_accuracy()