import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def gerar_dados_relatorio(dias=30):
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=dias),
        end=datetime.now(),
        freq="D"
    )
    
    data = []
    for date in dates:
        base_generation = 30 if date.weekday() < 5 else 25  
        weather_factor = np.random.uniform(0.7, 1.3)  
        
        gerado_total = base_generation * weather_factor
        consumido_total = np.random.uniform(20, 40)
        excedente = gerado_total - consumido_total
        
        data.append({
            "Data": date.strftime("%Y-%m-%d"),
            "Gerado (kWh)": round(gerado_total, 2),
            "Consumido (kWh)": round(consumido_total, 2),
            "Excedente (kWh)": round(excedente, 2),
            "Economia (R$)": round(excedente * 0.75, 2),
            "Eficiencia (%)": round((gerado_total / 50) * 100, 1),  # Eficiência baseada em capacidade máxima
            "Dia_Semana": date.strftime("%A"),
            "Mes": date.strftime("%B"),
            "Ano": date.year
        })
    
    return pd.DataFrame(data)

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