import matplotlib
import matplotlib.pyplot as plt
import io

matplotlib.use('Agg')

def generate_image_graphic(dados, titulo, tipo="bar"):
    """
    Gera a imagem do gráfico.
    Proporções mais 'panorâmicas' (achatadas) para economizar espaço vertical no Word.
    """
    if tipo == "pie":
        # Antes era (3.5, 2.5). Agora é mais largo e mais baixo.
        plt.figure(figsize=(4.5, 2.2)) 
    else:
        # Gráfico de barras mais baixo também
        plt.figure(figsize=(6, 3.5)) 
    
    chaves = [str(k)[:25] + ('...' if len(str(k)) > 25 else '') for k in dados.keys()]
    valores = list(dados.values())
    cores = ["#4F81BD", "#C0504D", "#9BBB59", "#11B23E", "#9E1FF3", "#E91E63", "#00BCD4", "#795548", "#FF9800", "#607D8B"]
    
    if tipo == "bar":
        plt.barh(chaves[::-1], valores[::-1], color='#5B9BD5', height=0.6)
        plt.title(titulo, pad=10, fontweight='bold', fontsize=8, fontname='Verdana')
        plt.yticks(fontsize=7, fontname='Verdana')
        plt.xticks(fontsize=7, fontname='Verdana')
        
    elif tipo == "pie":
        wedges, texts, autotexts = plt.pie(valores, autopct='%1.0f%%', startangle=90, colors=cores, textprops=dict(color="w", weight="bold", fontname='Verdana', size=6))
        # Ajustei o bbox_to_anchor para a legenda ficar mais coladinha na pizza e não gastar altura
        plt.legend(wedges, chaves, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, prop={'family': 'Verdana', 'size': 6})
        plt.title(titulo, pad=10, fontweight='bold', fontsize=8, fontname='Verdana')
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf