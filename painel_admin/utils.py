import io
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from fpdf import FPDF
from matplotlib.figure import Figure


def gerar_dados_relatorio(dias: int) -> pd.DataFrame:
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=dias), periods=dias, freq="D"
    )
    data = {
        "data": dates,
        "producao_kwh": np.random.uniform(15, 25, size=dias).round(2),
        "consumo_kwh": np.random.uniform(8, 20, size=dias).round(2),
        "injetado_kwh": np.random.uniform(5, 10, size=dias).round(2),
        "temperatura_media_c": np.random.uniform(22, 35, size=dias).round(1),
        "irradiancia_media_w_m2": np.random.uniform(4.0, 6.5, size=dias).round(2),
    }
    df = pd.DataFrame(data)
    df["economia_reais"] = df["producao_kwh"] * 0.75  # Custo hipotético do kWh
    df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")
    return df

def gerar_dados_por_periodo(tipo_periodo="mensal", meses=12):
    if tipo_periodo == "mensal":
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30*meses),
            end=datetime.now(),
            freq="M"
        )
        data = []
        for date in dates:
            gerado_mensal = np.random.uniform(800, 1200)
            consumido_mensal = np.random.uniform(700, 1000)
            data.append({
                "Periodo": date.strftime("%Y-%m"),
                "Gerado (kWh)": round(gerado_mensal, 2),
                "Consumido (kWh)": round(consumido_mensal, 2),
                "Excedente (kWh)": round(gerado_mensal - consumido_mensal, 2),
                "Economia (R$)": round((gerado_mensal - consumido_mensal) * 0.75, 2)
            })
        return pd.DataFrame(data)

def calcular_metricas_avancadas(df):
    total_gerado = df['Gerado (kWh)'].sum()
    total_consumido = df['Consumido (kWh)'].sum()
    total_excedente = df['Excedente (kWh)'].sum()
    
    metricas = {
        "total_gerado": total_gerado,
        "total_consumido": total_consumido,
        "total_excedente": total_excedente,
        "media_diaria_gerada": df['Gerado (kWh)'].mean(),
        "media_diaria_consumida": df['Consumido (kWh)'].mean(),
        "eficiencia_media": df['Eficiencia (%)'].mean(),
        "melhor_dia": df.loc[df['Gerado (kWh)'].idxmax(), 'Data'],
        "pior_dia": df.loc[df['Gerado (kWh)'].idxmin(), 'Data'],
        "dias_com_excedente": len(df[df['Excedente (kWh)'] > 0]),
        "percentual_excedente": (len(df[df['Excedente (kWh)'] > 0]) / len(df)) * 100
    }
    
    return metricas

def gerar_dados_comparativo(anos=2):
    data = []
    ano_base = datetime.now().year - anos + 1  
    
    for ano in range(ano_base, datetime.now().year + 1):
        for mes in range(1, 13):
            if ano == datetime.now().year and mes > datetime.now().month:
                break
            
            fator_crescimento = 1 + (ano - ano_base) * 0.05
            gerado = np.random.uniform(800, 1200) * fator_crescimento
            consumido = np.random.uniform(700, 1000)
            
            data.append({
                "Ano": ano,
                "Mes": mes,
                "Periodo": f"{ano}-{mes:02d}",
                "Gerado (kWh)": round(gerado, 2),
                "Consumido (kWh)": round(consumido, 2),
                "Excedente (kWh)": round(gerado - consumido, 2),
                "Economia (R$)": round((gerado - consumido) * 0.75, 2)
            })
    
    return pd.DataFrame(data) 


def gerar_pdf_relatorio(
    df: pd.DataFrame, incluir_graficos: bool, incluir_resumo: bool
) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    pdf.cell(0, 10, "Relatório de Desempenho Solar", 0, 1, "C")
    pdf.ln(10)

    if incluir_resumo:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Resumo Estatístico", 0, 1)
        pdf.set_font("Arial", "", 10)
        
        resumo_str = df.describe().to_string()
        pdf.multi_cell(0, 5, resumo_str)
        pdf.ln(10)

    if incluir_graficos:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Gráficos de Desempenho", 0, 1)
        pdf.ln(5)

        fig = Figure(figsize=(8, 4))
        ax = fig.subplots()
        ax.plot(df["data"], df["producao_kwh"], label="Produção (kWh)")
        ax.plot(df["data"], df["consumo_kwh"], label="Consumo (kWh)")
        ax.set_title("Produção vs. Consumo de Energia")
        ax.set_xlabel("Data")
        ax.set_ylabel("Energia (kWh)")
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        
        with io.BytesIO() as buffer:
            fig.savefig(buffer, format="png")
            pdf.image(buffer, x=pdf.get_x(), y=pdf.get_y(), w=180)
        pdf.ln(100)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Dados Completos", 0, 1)
    pdf.set_font("Arial", "", 8)

    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.5

    for col in df.columns:
        pdf.cell(col_width, row_height, col, border=1)
    pdf.ln(row_height)

    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)

    return bytes(pdf.output()) 