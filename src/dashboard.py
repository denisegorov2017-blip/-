#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивный дашборд Streamlit для анализа результатов.

Для запуска: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import webbrowser

# Настройка страницы
st.set_page_config(
    layout="wide", 
    page_title="Дашборд Расчета Усушки", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Добавляем пользовательские стили с современным дизайном
st.markdown("""
<style>
    /* Градиентный заголовок */
    .main-header {
        background: linear-gradient(135deg, #2c3e50, #4a6491, #2c3e50);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
        transform: rotate(30deg);
    }
    
    /* Карточки метрик с улучшенным дизайном */
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        text-align: center;
        height: 100%;
        border: 1px solid #e9ecef;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #3498db, #2980b9);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #2c3e50;
        margin: 15px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover .metric-value {
        transform: scale(1.05);
    }
    
    .metric-label {
        font-size: 16px;
        color: #6c757d;
        font-weight: 600;
    }
    
    /* Панель информации */
    .info-card {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-left: 8px solid #2196f3;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .info-card::after {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 70%);
        transform: translate(40%, -40%);
    }
    
    /* Кнопки отчетов */
    .report-buttons {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 25px;
        border-radius: 15px;
        margin: 25px 0;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .report-buttons::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #4caf50, #2e7d32);
    }
    
    /* Секции с заголовками */
    .section-header {
        background: linear-gradient(90deg, #f8f9fa, #e9ecef);
        padding: 20px;
        border-radius: 15px;
        margin: 25px 0 20px 0;
        border-left: 6px solid #007bff;
        box-shadow: 0 3px 10px rgba(0,123,255,0.1);
        display: flex;
        align-items: center;
    }
    
    .section-header h2 {
        margin: 0;
        font-weight: 700;
        color: #2c3e50;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        padding: 10px;
        background: linear-gradient(180deg, #f8f9fa, #e9ecef);
        border-radius: 12px 12px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 10px 10px 0 0;
        gap: 1px;
        padding: 12px 20px;
        font-weight: 600;
        color: #6c757d;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        box-shadow: 0 4px 10px rgba(0,123,255,0.3);
        transform: translateY(-2px);
    }
    
    /* Фильтры в сайдбаре */
    [data-testid=stSidebar] {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-right: 1px solid #dee2e6;
        padding: 20px;
    }
    
    [data-testid=stSidebar] .stMarkdown {
        padding: 15px;
        border-radius: 10px;
        background: rgba(255,255,255,0.7);
        margin-bottom: 15px;
    }
    
    /* Кнопки */
    .stButton>button {
        border-radius: 10px;
        height: 3.8rem;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Таблицы */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .stDataFrame th {
        background: linear-gradient(180deg, #3498db, #2980b9);
        color: white;
    }
    
    .stDataFrame tr:nth-child(even) {
        background-color: #f8fafc;
    }
    
    .stDataFrame tr:hover {
        background-color: #e3f2fd;
        transition: background-color 0.3s ease;
    }
    
    /* Селектбоксы */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .stSelectbox div[data-baseweb="select"]:hover {
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Слайдеры */
    .stSlider div[data-baseweb="slider"] {
        height: 35px;
    }
    
    .stSlider div[data-baseweb="slider"] [role="slider"] {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #007bff;
        box-shadow: 0 2px 8px rgba(0,123,255,0.4);
        transition: all 0.3s ease;
    }
    
    .stSlider div[data-baseweb="slider"] [role="slider"]:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0,123,255,0.6);
    }
    
    /* Навигационное меню */
    .nav-menu {
        display: flex;
        background: linear-gradient(135deg, #2c3e50, #4a6491);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .nav-item {
        flex: 1;
        text-align: center;
        padding: 15px;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-item:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-3px);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #3498db, #2980b9);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Карточки данных */
    .data-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid #eef2f7;
        transition: all 0.3s ease;
    }
    
    .data-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        transform: translateY(-3px);
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out forwards;
    }
    
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .nav-menu {
            flex-direction: column;
        }
        
        .metric-card {
            margin-bottom: 20px;
        }
        
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
        }
        
        .section-header h2 {
            font-size: 20px;
        }
        
        .main-header {
            padding: 20px;
        }
        
        .main-header h1 {
            font-size: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Заголовок с градиентом
st.markdown('''<div class="main-header">
    <h1>📊 Интерактивный дашборд анализа усушки</h1>
    <p style="font-size: 20px; opacity: 0.95; margin-top: 15px; font-weight: 300;">Анализ и визуализация коэффициентов нелинейной усушки продукции</p>
</div>''', unsafe_allow_html=True)

# Навигационное меню
st.markdown('''
<div class="nav-menu">
    <div class="nav-item active">📈 Анализ данных</div>
    <div class="nav-item">📊 Визуализация</div>
    <div class="nav-item">📋 Отчеты</div>
    <div class="nav-item">ℹ️ О системе</div>
</div>
''', unsafe_allow_html=True)

# Информационная панель
with st.expander("ℹ️ О системе", expanded=False):
    st.markdown("""
    ### 📊 Система расчета коэффициентов нелинейной усушки
    
    Данная система позволяет:
    - 📊 Анализировать коэффициенты усушки для различных видов продукции
    - 🔍 Фильтровать данные по точности расчетов
    - 📈 Визуализировать зависимости между коэффициентами
    - 🔎 Поискать конкретные позиции по названию
    
    **Типы обработки:**
    - 🐟 **Х/К** - Холодное копчение
    - 🐟 **Г/К** - Горячее копчение
    - 🐟 **С/с** - Слабосоленая рыба
    
    ---
    
    💡 **Совет:** Используйте фильтры в левой панели для точной настройки отображаемых данных
    """)

# --- Загрузка данных ---
@st.cache_data
def load_data(file_path):
    try:
        # Используем pandas, т.к. streamlit лучше всего с ним интегрирован для отображения
        df = pd.read_html(file_path, encoding="utf-8")[0]
        return df
    except Exception as e:
        st.error(f"Не удалось загрузить данные из отчета: {e}")
        return pd.DataFrame()

# --- Выбор файла --- 
output_dir = "результаты"
if os.path.exists(output_dir):
    # Get all report files
    all_report_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
    
    # Categorize reports
    coefficient_reports = [f for f in all_report_files if f.startswith('коэффициенты')]
    error_reports = [f for f in all_report_files if f.startswith('ошибки')]
    no_inventory_reports = [f for f in all_report_files if f.startswith('позиции_без_инвентаризации')]
    model_comparison_reports = [f for f in all_report_files if f.startswith('сравнение_моделей')]
    nomenclature_performance_reports = [f for f in all_report_files if f.startswith('производительность_номенклатур')]
    
    # Use coefficient reports as the main reports for selection
    report_files = coefficient_reports
    
    if report_files:
        # Улучшенный выбор файла с описанием
        st.markdown('<div class="section-header"><h2>📂 Выбор отчета для анализа</h2></div>', unsafe_allow_html=True)
        
        # Информационная карточка с количеством отчетов
        st.markdown(f'''
        <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #2196f3;">
            <h4 style="margin: 0 0 10px 0; color: #1a237e;">📊 Доступные отчеты</h4>
            <p style="margin: 0; font-size: 18px; font-weight: 700;">Всего отчетов: {len(report_files)}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">Выберите один из доступных отчетов для анализа</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Добавляем информацию о количестве доступных отчетов
        st.info(f"Доступно отчетов: {len(report_files)}")
        
        selected_report = st.selectbox(
            "Выберите отчет для анализа:", 
            report_files, 
            key="report_selector",
            help="Выберите один из доступных отчетов для анализа данных"
        )
        report_path = os.path.join(output_dir, selected_report)
        
        # Кнопки для открытия отчетов с улучшенным дизайном
        st.markdown('<div class="report-buttons">', unsafe_allow_html=True)
        st.markdown("<h3>🚀 Быстрый доступ к отчетам</h3><p style='margin-top: 10px; opacity: 0.8;'>Откройте отчеты одним кликом для детального анализа</p>", unsafe_allow_html=True)
        
        # Create columns for report buttons
        cols = st.columns(3)
        
        with cols[0]:
            if st.button("📖 Открыть выбранный отчет", use_container_width=True):
                try:
                    os.startfile(os.path.abspath(report_path))  # Для Windows
                    st.success("Отчет открыт в браузере")
                except Exception as e:
                    st.error(f"Не удалось открыть отчет: {e}")
        
        with cols[1]:
            if st.button("📁 Открыть папку с отчетами", use_container_width=True):
                try:
                    os.startfile(os.path.abspath(output_dir))  # Для Windows
                    st.success("Папка с отчетами открыта")
                except Exception as e:
                    st.error(f"Не удалось открыть папку: {e}")
        
        with cols[2]:
            if st.button("📋 Все отчеты", use_container_width=True):
                st.session_state.show_all_reports = not st.session_state.get("show_all_reports", False)
        
        # Show all reports if button is clicked
        if st.session_state.get("show_all_reports", False):
            st.markdown("---")
            st.subheader("Все доступные отчеты")
            
            # Coefficient reports
            if coefficient_reports:
                st.markdown("**📊 Отчеты по коэффициентам усушки:**")
                for report in coefficient_reports[:5]:  # Show first 5
                    report_path_full = os.path.join(output_dir, report)
                    if st.button(f"📊 {report}", key=f"coeff_{report}"):
                        try:
                            os.startfile(os.path.abspath(report_path_full))
                            st.success(f"Отчет {report} открыт в браузере")
                        except Exception as e:
                            st.error(f"Не удалось открыть отчет: {e}")
                if len(coefficient_reports) > 5:
                    st.caption(f"... и еще {len(coefficient_reports) - 5} отчетов")
            
            # Error reports
            if error_reports:
                st.markdown("**⚠️ Отчеты об ошибках:**")
                for report in error_reports[:5]:  # Show first 5
                    report_path_full = os.path.join(output_dir, report)
                    if st.button(f"⚠️ {report}", key=f"error_{report}"):
                        try:
                            os.startfile(os.path.abspath(report_path_full))
                            st.success(f"Отчет {report} открыт в браузере")
                        except Exception as e:
                            st.error(f"Не удалось открыть отчет: {e}")
                if len(error_reports) > 5:
                    st.caption(f"... и еще {len(error_reports) - 5} отчетов")
            
            # No inventory reports
            if no_inventory_reports:
                st.markdown("**📦 Отчеты по позициям без инвентаризации:**")
                for report in no_inventory_reports[:5]:  # Show first 5
                    report_path_full = os.path.join(output_dir, report)
                    if st.button(f"📦 {report}", key=f"no_inv_{report}"):
                        try:
                            os.startfile(os.path.abspath(report_path_full))
                            st.success(f"Отчет {report} открыт в браузере")
                        except Exception as e:
                            st.error(f"Не удалось открыть отчет: {e}")
                if len(no_inventory_reports) > 5:
                    st.caption(f"... и еще {len(no_inventory_reports) - 5} отчетов")
            
            # Model comparison reports
            if model_comparison_reports:
                st.markdown("**🔬 Отчеты о сравнении моделей:**")
                for report in model_comparison_reports[:5]:  # Show first 5
                    report_path_full = os.path.join(output_dir, report)
                    if st.button(f"🔬 {report}", key=f"model_{report}"):
                        try:
                            os.startfile(os.path.abspath(report_path_full))
                            st.success(f"Отчет {report} открыт в браузере")
                        except Exception as e:
                            st.error(f"Не удалось открыть отчет: {e}")
                if len(model_comparison_reports) > 5:
                    st.caption(f"... и еще {len(model_comparison_reports) - 5} отчетов")
            
            # Nomenclature performance reports
            if nomenclature_performance_reports:
                st.markdown("**📈 Отчеты о производительности номенклатур:**")
                for report in nomenclature_performance_reports[:5]:  # Show first 5
                    report_path_full = os.path.join(output_dir, report)
                    if st.button(f"📈 {report}", key=f"perf_{report}"):
                        try:
                            os.startfile(os.path.abspath(report_path_full))
                            st.success(f"Отчет {report} открыт в браузере")
                        except Exception as e:
                            st.error(f"Не удалось открыть отчет: {e}")
                if len(nomenclature_performance_reports) > 5:
                    st.caption(f"... и еще {len(nomenclature_performance_reports) - 5} отчетов")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Загрузка данных
        with st.spinner("Загрузка данных из отчета..."):
            data = load_data(report_path)

        if not data.empty:
            st.markdown('<div class="section-header"><h2>📈 Анализ данных</h2></div>', unsafe_allow_html=True)

            # --- Фильтры в сайдбаре ---
            with st.sidebar:
                st.header("⚙️ Фильтры")
                
                # Информационная панель фильтров
                st.markdown('<div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px;">'
                           '<h4>🎛️ Настройка фильтров</h4>'
                           '<p>Используйте фильтры для анализа подмножества данных</p></div>', 
                           unsafe_allow_html=True)
                
                min_accuracy = st.slider(
                    "Минимальная точность (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=80.0, 
                    step=1.0,
                    help="Отображать только записи с точностью выше указанного значения"
                )
                
                search_text = st.text_input(
                    "Поиск по номенклатуре",
                    help="Введите часть названия для поиска"
                )
                
                # Дополнительные фильтры
                st.markdown("---")
                st.subheader("🔬 Расширенные фильтры")
                
                # Фильтр по диапазону коэффициента A
                if 'a' in data.columns:
                    # Convert to numeric first to handle non-numeric values like '—'
                    data['a'] = pd.to_numeric(data['a'], errors='coerce')
                    min_a_val = float(data['a'].min())
                    max_a_val = float(data['a'].max())
                    # Handle case where min and max are the same or NaN
                    if min_a_val == max_a_val or pd.isna(min_a_val) or pd.isna(max_a_val):
                        min_a_val = 0.0 if pd.isna(min_a_val) else min_a_val - 0.1 if min_a_val > 0.1 else 0.0
                        max_a_val = 1.0 if pd.isna(max_a_val) else max_a_val + 0.1
                    min_a, max_a = st.slider(
                        "Диапазон коэффициента A",
                        min_a_val, 
                        max_a_val,
                        (min_a_val, max_a_val),
                        help="Ограничить отображение по значению коэффициента A"
                    )
                
                # Фильтр по диапазону коэффициента B
                if 'b (день⁻¹)' in data.columns:
                    # Convert to numeric first to handle non-numeric values like '—'
                    data['b (день⁻¹)'] = pd.to_numeric(data['b (день⁻¹)'], errors='coerce')
                    min_b_val = float(data['b (день⁻¹)'].min())
                    max_b_val = float(data['b (день⁻¹)'].max())
                    # Handle case where min and max are the same or NaN
                    if min_b_val == max_b_val or pd.isna(min_b_val) or pd.isna(max_b_val):
                        min_b_val = 0.0 if pd.isna(min_b_val) else min_b_val - 0.1 if min_b_val > 0.1 else 0.0
                        max_b_val = 1.0 if pd.isna(max_b_val) else max_b_val + 0.1
                    min_b, max_b = st.slider(
                        "Диапазон коэффициента B",
                        min_b_val, 
                        max_b_val,
                        (min_b_val, max_b_val),
                        help="Ограничить отображение по значению коэффициента B"
                    )

            # --- Преобразование данных ---
            # Преобразуем столбцы в числовые типы (already done above, but keeping for clarity)
            data['Точность (%)'] = pd.to_numeric(data['Точность (%)'], errors='coerce')
            # data['a'] = pd.to_numeric(data['a'], errors='coerce')  # Already converted above
            # data['b (день⁻¹)'] = pd.to_numeric(data['b (день⁻¹)'], errors='coerce')  # Already converted above
            
            # Применяем фильтры
            filtered_data = data.copy()
            
            # Фильтрация по точности
            if 'Точность (%)' in filtered_data.columns:
                valid_accuracy_data = filtered_data.dropna(subset=['Точность (%)'])
                filtered_data = valid_accuracy_data[valid_accuracy_data['Точность (%)'] >= min_accuracy]
            
            # Фильтрация по поиску
            if search_text:
                filtered_data = filtered_data[filtered_data['Номенклатура'].str.contains(search_text, case=False, na=False)]
            
            # Фильтрация по коэффициенту A
            if 'a' in filtered_data.columns and 'a' in data.columns:
                filtered_data = filtered_data[
                    (filtered_data['a'] >= min_a) & 
                    (filtered_data['a'] <= max_a)
                ]
            
            # Фильтрация по коэффициенту B
            if 'b (день⁻¹)' in filtered_data.columns and 'b (день⁻¹)' in data.columns:
                filtered_data = filtered_data[
                    (filtered_data['b (день⁻¹)'] >= min_b) & 
                    (filtered_data['b (день⁻¹)'] <= max_b)
                ]

            # --- Информационная панель ---
            st.markdown('''
            <div class="info-card">
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                    <div style="text-align: center; padding: 10px;">
                        <h4 style="margin: 0 0 10px 0; color: #1a237e;">📂 Выбранный файл</h4>
                        <p style="margin: 0; font-size: 16px; font-weight: 600;">{selected_report}</p>
                    </div>
                    <div style="text-align: center; padding: 10px;">
                        <h4 style="margin: 0 0 10px 0; color: #1a237e;">📊 Всего записей</h4>
                        <p style="margin: 0; font-size: 24px; font-weight: 800; color: #2196f3;">{len(data)}</p>
                    </div>
                    <div style="text-align: center; padding: 10px;">
                        <h4 style="margin: 0 0 10px 0; color: #1a237e;">🔍 После фильтрации</h4>
                        <p style="margin: 0; font-size: 24px; font-weight: 800; color: #4caf50;">{len(filtered_data)}</p>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # --- Статистика ---
            st.markdown('<div class="section-header"><h2>📊 Сводная статистика</h2></div>', unsafe_allow_html=True)
            
            if not filtered_data.empty:
                # Расчет метрик
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                
                # Добавляем анимацию для карточек метрик
                st.markdown("""
                <style>
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                .metric-card {
                    animation: fadeInUp 0.6s ease-out forwards;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Всего позиций
                with metrics_col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Всего позиций</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{len(filtered_data)}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Средний коэффициент A
                with metrics_col2:
                    if 'a' in filtered_data.columns:
                        avg_a = filtered_data['a'].dropna().mean()
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Средний коэф. A</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{avg_a:.3f}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Средний коэффициент B
                with metrics_col3:
                    if 'b (день⁻¹)' in filtered_data.columns:
                        avg_b = filtered_data['b (день⁻¹)'].dropna().mean()
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Средний коэф. B</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{avg_b:.3f}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Средняя точность
                with metrics_col4:
                    if 'Точность (%)' in filtered_data.columns:
                        avg_accuracy = filtered_data['Точность (%)'].dropna().mean()
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Средняя точность</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{avg_accuracy:.1f}%</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                # --- Отображение данных ---
                st.markdown('<div class="section-header"><h2>📋 Результаты фильтрации</h2></div>', unsafe_allow_html=True)
                
                # Добавляем пояснение к таблице
                st.markdown("""
                <div style="background: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; margin-bottom: 20px;">
                    <p style="margin: 0; color: #856404;"><strong>ℹ️ Подсказка:</strong> Вы можете сортировать данные, кликая по заголовкам столбцов. Используйте фильтры в левой панели для точной настройки отображаемых данных.</p>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(filtered_data, use_container_width=True)
                
                # --- Визуализация ---
                st.markdown('<div class="section-header"><h2>📉 Визуализация</h2></div>', unsafe_allow_html=True)
                
                # Добавляем пояснение к визуализации
                st.markdown("""
                <div style="background: #d1ecf1; padding: 15px; border-radius: 10px; border-left: 5px solid #0c5460; margin-bottom: 20px;">
                    <p style="margin: 0; color: #0c5460;"><strong>📊 Интерактивные графики:</strong> Все графики интерактивны. Наведите курсор для получения дополнительной информации, используйте инструменты масштабирования и перемещения.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Tabs для разных типов визуализации
                viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📈 Точность", "🔄 Коэффициенты", "📋 Детали"])
                
                with viz_tab1:
                    st.subheader("📊 Распределение точности")
                    # Проверяем, есть ли данные для визуализации
                    if not filtered_data.empty and 'Точность (%)' in filtered_data.columns and not filtered_data['Точность (%)'].isna().all():
                        # Убираем строки с NaN значениями
                        accuracy_data = filtered_data['Точность (%)'].dropna()
                        if len(accuracy_data) > 0:
                            # Гистограмма распределения точности
                            fig_hist = px.histogram(filtered_data, x='Точность (%)', 
                                                  nbins=20, 
                                                  title='Распределение точности расчетов',
                                                  labels={'Точность (%)': 'Точность (%)', 'count': 'Количество'},
                                                  color_discrete_sequence=['#2196f3'])
                            fig_hist.update_layout(bargap=0.1, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig_hist, use_container_width=True)
                            
                            # Дополнительная визуализация точности
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Статистика точности:**")
                                st.write(f"- Минимальная: {accuracy_data.min():.1f}%")
                                st.write(f"- Максимальная: {accuracy_data.max():.1f}%")
                                st.write(f"- Средняя: {accuracy_data.mean():.1f}%")
                                st.write(f"- Медиана: {accuracy_data.median():.1f}%")
                            
                            with col2:
                                # Круговая диаграмма по категориям точности
                                high_acc = len(accuracy_data[accuracy_data >= 95])
                                med_acc = len(accuracy_data[(accuracy_data >= 80) & (accuracy_data < 95)])
                                low_acc = len(accuracy_data[accuracy_data < 80])
                                
                                fig_pie = px.pie(values=[high_acc, med_acc, low_acc], 
                                               names=['Высокая (≥95%)', 'Средняя (80-95%)', 'Низкая (<80%)'],
                                               title='Распределение по категориям точности',
                                               color_discrete_sequence=['#4caf50', '#ff9800', '#f44336'])
                                st.plotly_chart(fig_pie, use_container_width=True)
                        else:
                            st.info("Нет данных для отображения графика точности")
                    else:
                        st.info("Нет данных для отображения графика точности")
                
                with viz_tab2:
                    st.subheader("🔄 Зависимость коэффициентов")
                    # Проверяем, есть ли данные для визуализации
                    if not filtered_data.empty and 'a' in filtered_data.columns and 'b (день⁻¹)' in filtered_data.columns:
                        # Убираем строки с NaN значениями
                        chart_data = filtered_data.dropna(subset=['a', 'b (день⁻¹)'])
                        if not chart_data.empty:
                            # Диаграмма рассеяния
                            fig_scatter = px.scatter(chart_data, x="a", y="b (день⁻¹)", 
                                                   hover_data=['Номенклатура'],
                                                   title='Корреляция между коэффициентами A и B',
                                                   labels={'a': 'Коэффициент A', 'b (день⁻¹)': 'Коэффициент B (день⁻¹)'},
                                                   color='Точность (%)',
                                                   color_continuous_scale='viridis')
                            fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig_scatter, use_container_width=True)
                            
                            # Дополнительная информация
                            correlation = chart_data['a'].corr(chart_data['b (день⁻¹)'])
                            st.write("**Анализ коэффициентов:**")
                            st.write(f"- Корреляция: {correlation:.3f}")
                            
                            # Гистограммы для каждого коэффициента
                            col1, col2 = st.columns(2)
                            with col1:
                                fig_a = px.histogram(chart_data, x='a', nbins=20, 
                                                   title='Распределение коэффициента A',
                                                   labels={'a': 'Коэффициент A', 'count': 'Количество'},
                                                   color_discrete_sequence=['#e91e63'])
                                fig_a.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                                st.plotly_chart(fig_a, use_container_width=True)
                            
                            with col2:
                                fig_b = px.histogram(chart_data, x='b (день⁻¹)', nbins=20,
                                                   title='Распределение коэффициента B',
                                                   labels={'b (день⁻¹)': 'Коэффициент B (день⁻¹)', 'count': 'Количество'},
                                                   color_discrete_sequence=['#9c27b0'])
                                fig_b.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                                st.plotly_chart(fig_b, use_container_width=True)
                        else:
                            st.info("Нет данных для отображения графика зависимости коэффициентов")
                    else:
                        st.info("Нет данных для отображения графика зависимости коэффициентов")
                
                with viz_tab3:
                    st.subheader("📋 Детальная информация")
                    if not filtered_data.empty:
                        # Показываем топ-10 позиций по точности
                        if 'Точность (%)' in filtered_data.columns:
                            top_accuracy = filtered_data.nlargest(10, 'Точность (%)')
                            st.write("**Топ-10 по точности:**")
                            st.dataframe(top_accuracy[['Номенклатура', 'Точность (%)']], use_container_width=True)
                        
                        # Показываем топ-10 по коэффициенту 'a'
                        if 'a' in filtered_data.columns:
                            top_a = filtered_data.nlargest(10, 'a')
                            st.write("**Топ-10 по коэффициенту 'a':**")
                            st.dataframe(top_a[['Номенклатура', 'a']], use_container_width=True)
                        
                        # Таблица с полной информацией
                        st.write("**Полные данные:**")
                        st.dataframe(filtered_data, use_container_width=True)

            else:
                st.warning("После применения фильтров не осталось данных для отображения")

    else:
        st.warning("В папке 'результаты' не найдено файлов отчетов по коэффициентам.")
else:
    st.error("Папка 'результаты' не найдена. Сначала выполните расчет.")