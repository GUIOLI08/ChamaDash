import matplotlib
import matplotlib.pyplot as plt
import io

matplotlib.use('Agg')

def generate_image_graphic(dados, titulo, tipo="bar"):
    """
    Gera a imagem do gráfico.
    Proporções travadas para garantir o exato mesmo tamanho lado a lado.
    """
    buf = io.BytesIO()
    chaves = [str(k)[:25] + ('...' if len(str(k)) > 25 else '') for k in dados.keys()]
    valores = list(dados.values())
    cores = ["#4F81BD", "#C0504D", "#9BBB59", "#11B23E", "#9E1FF3", "#E91E63", "#00BCD4", "#795548", "#FF9800", "#607D8B"]
    
    if tipo == "pie":
        fig = plt.figure(figsize=(3.5, 3.0)) 
        wedges, texts, autotexts = plt.pie(valores, autopct='%1.0f%%', startangle=90, colors=cores, textprops=dict(color="w", weight="bold", fontname='Verdana', size=7))
        plt.legend(wedges, chaves, loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=1, prop={'family': 'Verdana', 'size': 7})
        plt.title(titulo, pad=15, fontweight='bold', fontsize=9, fontname='Verdana')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.25)
        
        plt.savefig(buf, format='png', dpi=120) 
        
    elif tipo == "bar":
        plt.figure(figsize=(6, 3.2)) 
        plt.barh(chaves[::-1], valores[::-1], color='#5B9BD5', height=0.6)
        plt.title(titulo, pad=10, fontweight='bold', fontsize=8, fontname='Verdana')
        plt.yticks(fontsize=7, fontname='Verdana')
        plt.xticks(fontsize=7, fontname='Verdana')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        
    buf.seek(0)
    plt.close()
    return buf