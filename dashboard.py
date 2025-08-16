import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import numpy as np
import json

# ========== CONFIGURAÇÃO PARA PRODUÇÃO ==========
def setup_for_production():
    """Configurações específicas para deploy em produção"""
    
    # Detectar se está em ambiente de deploy
    is_production = (
        os.getenv('STREAMLIT_SERVER_PORT') or 
        os.getenv('PORT') or 
        os.getenv('RAILWAY_ENVIRONMENT') or
        os.getenv('HEROKU_APP_NAME') or
        os.getenv('GAE_ENV') or
        os.getenv('RENDER') or
        os.getenv('VERCEL') or
        os.getenv('DOCKER_CONTAINER')
    )
    
    if is_production:
        # Configurações para deploy
        port = os.getenv('PORT', '8501')
        os.environ['STREAMLIT_SERVER_PORT'] = port
        os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
        os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
        
        # Log do ambiente
        print(f"🚀 Rodando em produção na porta {port}")
        return True
    else:
        print("🏠 Rodando em ambiente local")
        return False

# Executar setup imediatamente
IS_PRODUCTION = setup_for_production()

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(
    page_title="TrendX Analytics - Versão Completa",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "TrendX Analytics - Dashboard com Métricas Reais das Redes Sociais"
    }
)

# ========== CSS AVANÇADO ==========
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .ranking-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
    }
    
    .ranking-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    
    .video-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .zero-user-card {
        background: linear-gradient(145deg, #fff3cd, #fef3cd);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
        opacity: 0.8;
    }
    
    .insight-box {
        background: linear-gradient(145deg, #e3f2fd, #f3e5f5);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #2196f3;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(145deg, #fff3e0, #fce4ec);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #ff9800;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(145deg, #e8f5e8, #f1f8e9);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #4caf50;
        margin: 1rem 0;
    }
    
    .stats-box {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    
    .production-banner {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
        font-size: 0.9em;
    }
    
    .ranking-header {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
    
    .ranking-item {
        background: white;
        padding: 0.7rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        font-size: 0.9em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    
    .ranking-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        padding: 12px 20px;
        font-weight: 600;
    }
    
    /* Otimizações para mobile */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        .metric-card {
            padding: 1rem;
        }
        
        /* Rankings em mobile: 2x2 em vez de 4x1 */
        [data-testid="column"]:nth-child(n+3) {
            margin-top: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        /* Rankings em telas muito pequenas: 1 coluna */
        [data-testid="column"] {
            margin-bottom: 1rem;
        }
        
        .ranking-header h4 {
            font-size: 1rem;
        }
        
        .ranking-item {
            font-size: 0.8em;
            padding: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== CONFIGURAÇÕES ==========
DB_PATH = "trendx_bot.db"

# TTL otimizado baseado no ambiente
CACHE_TTL = 300 if not IS_PRODUCTION else 600  # 5 min local, 10 min produção

# ========== FUNÇÕES UTILITÁRIAS AVANÇADAS ==========
def converter_para_numerico_seguro(series, valor_padrao=0):
    """Converte uma série para numérico de forma segura"""
    try:
        return pd.to_numeric(series, errors='coerce').fillna(valor_padrao)
    except:
        return pd.Series([valor_padrao] * len(series), index=series.index)

def formatar_numero(num):
    """Formatar números para exibição"""
    try:
        if pd.isna(num) or num == 0:
            return "0"
        
        # Converter para float se for categórico ou string
        if isinstance(num, (str, pd.Categorical)):
            try:
                num = float(num)
            except:
                return "0"
        
        if num >= 1000000000:
            return f"{num/1000000000:.1f}B"
        elif num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return f"{int(num):,}"
    except:
        return "0"

def calcular_engajamento_por_plataforma(views, likes, comments, shares, platform):
    """Calcula engajamento usando as fórmulas oficiais de cada rede social"""
    if views == 0:
        return 0
    
    if platform.lower() == 'tiktok':
        # TikTok: (Curtidas + Comentários + Compartilhamentos) / Views × 100
        # TikTok considera todas as interações igualmente
        engajamento = ((likes + comments + shares) / views) * 100
    
    elif platform.lower() == 'youtube':
        # YouTube: (Curtidas + Comentários) / Views × 100
        # YouTube não conta shares da mesma forma
        engajamento = ((likes + comments) / views) * 100
    
    elif platform.lower() == 'instagram':
        # Instagram: (Curtidas + Comentários + Compartilhamentos) / Alcance × 100
        # Instagram usa alcance, mas como temos views, usamos views
        engajamento = ((likes + comments + shares) / views) * 100
    
    else:
        # Fórmula geral para outras plataformas
        engajamento = ((likes + comments + shares) / views) * 100
    
    return round(engajamento, 2)

def calcular_score_performance_real(views, likes, comments, shares, videos, platform_principal=None):
    """Calcula score baseado nas métricas reais das redes sociais"""
    if views == 0 or videos == 0:
        return 0
    
    # 1. Taxa de Engajamento Real (50% do score)
    if platform_principal:
        taxa_engajamento = calcular_engajamento_por_plataforma(views, likes, comments, shares, platform_principal)
    else:
        # Fórmula geral se não soubermos a plataforma principal
        taxa_engajamento = ((likes + comments + shares) / views) * 100
    
    # Normalizar taxa de engajamento para pontuação (0-50 pontos)
    # Taxa > 10% = pontuação máxima (50 pontos)
    score_engajamento = min(taxa_engajamento * 5, 50)
    
    # 2. Volume de Alcance (30% do score)
    # Baseado em views totais, mas com escala logarítmica
    score_volume = min(np.log1p(views) * 3, 30)
    
    # 3. Frequência/Consistência (20% do score)
    # Views por vídeo - mede se cada vídeo tem performance boa
    views_por_video = views / videos
    score_consistencia = min(views_por_video * 0.002, 20)
    
    total_score = score_engajamento + score_volume + score_consistencia
    return min(round(total_score, 1), 100)

def determinar_plataforma_principal(tiktok_views, youtube_views, instagram_views):
    """Determina qual é a plataforma principal do usuário"""
    plataformas = {
        'tiktok': tiktok_views,
        'youtube': youtube_views, 
        'instagram': instagram_views
    }
    
    # Retorna a plataforma com mais views
    plataforma_principal = max(plataformas.items(), key=lambda x: x[1])
    return plataforma_principal[0] if plataforma_principal[1] > 0 else None

def obter_categoria_performance(score):
    """Retorna categoria baseada no score"""
    if score >= 80:
        return "🏆 Elite", "#ffd700"
    elif score >= 60:
        return "🥇 Expert", "#c0c0c0"
    elif score >= 40:
        return "🥈 Avançado", "#cd7f32"
    elif score >= 20:
        return "🥉 Intermediário", "#4caf50"
    elif score > 0:
        return "🌱 Iniciante", "#ff9800"
    else:
        return "😴 Inativo", "#6c757d"

def conectar_banco():
    """Conecta com o banco de dados"""
    if not os.path.exists(DB_PATH):
        st.error(f"⚠️ Banco de dados não encontrado: {DB_PATH}")
        if IS_PRODUCTION:
            st.error("🚨 **ERRO DE DEPLOY:** Banco de dados não está no servidor!")
            st.info("🔧 **Para corrigir:**")
            st.info("1. Certifique-se que o arquivo trendx_bot.db está no repositório")
            st.info("2. Verifique se o arquivo não está no .gitignore") 
            st.info("3. O arquivo deve estar na raiz do projeto")
            st.info("4. Faça um novo deploy incluindo o banco")
        return None
    return sqlite3.connect(DB_PATH)

@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_usuarios_completo():
    """Carrega TODOS os usuários (incluindo com zeros)"""
    conn = conectar_banco()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT 
            user_id,
            discord_username,
            COALESCE(total_videos, 0) as total_videos,
            COALESCE(total_views, 0) as total_views,
            COALESCE(total_likes, 0) as total_likes,
            COALESCE(total_comments, 0) as total_comments,
            COALESCE(total_shares, 0) as total_shares,
            COALESCE(tiktok_views, 0) as tiktok_views,
            COALESCE(tiktok_videos, 0) as tiktok_videos,
            COALESCE(youtube_views, 0) as youtube_views,
            COALESCE(youtube_videos, 0) as youtube_videos,
            COALESCE(instagram_views, 0) as instagram_views,
            COALESCE(instagram_videos, 0) as instagram_videos,
            updated_at
        FROM cached_stats 
        WHERE discord_username IS NOT NULL 
        AND discord_username != ''
        ORDER BY total_views DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return df
        
        # Converter todas as colunas numéricas de forma segura
        numeric_columns = ['total_videos', 'total_views', 'total_likes', 'total_comments', 'total_shares',
                          'tiktok_views', 'tiktok_videos', 'youtube_views', 'youtube_videos', 
                          'instagram_views', 'instagram_videos']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = converter_para_numerico_seguro(df[col], 0)
        
        # Calcular métricas avançadas
        df['total_interactions'] = df['total_likes'] + df['total_comments'] + df['total_shares']
        
        # Garantir que não há divisão por zero e converter para float
        df['total_views'] = pd.to_numeric(df['total_views'], errors='coerce').fillna(0)
        df['total_videos'] = pd.to_numeric(df['total_videos'], errors='coerce').fillna(0)
        df['total_interactions'] = pd.to_numeric(df['total_interactions'], errors='coerce').fillna(0)
        
        # Calcular taxa de engajamento por plataforma (usando fórmulas reais)
        df['plataforma_principal'] = df.apply(
            lambda x: determinar_plataforma_principal(
                x['tiktok_views'], x['youtube_views'], x['instagram_views']
            ), axis=1
        )
        
        # Taxa de engajamento usando fórmulas reais das redes sociais
        df['taxa_engajamento'] = df.apply(
            lambda x: calcular_engajamento_por_plataforma(
                x['total_views'], x['total_likes'], x['total_comments'], 
                x['total_shares'], x['plataforma_principal'] or 'geral'
            ), axis=1
        )
        
        # Score de performance usando métricas reais
        df['score_performance'] = df.apply(
            lambda x: calcular_score_performance_real(
                x['total_views'], x['total_likes'], x['total_comments'], 
                x['total_shares'], x['total_videos'], x['plataforma_principal']
            ), axis=1
        ).round(1)
        
        # Métricas complementares
        df['media_views_por_video'] = (df['total_views'] / df['total_videos'].replace(0, 1)).round(0)
        df['media_likes_por_video'] = (df['total_likes'] / df['total_videos'].replace(0, 1)).round(0)
        df['media_comments_por_video'] = (df['total_comments'] / df['total_videos'].replace(0, 1)).round(2)
        
        # Categoria de performance
        df[['categoria_performance', 'cor_categoria']] = df['score_performance'].apply(
            lambda x: pd.Series(obter_categoria_performance(x))
        )
        
        # Rankings (só para usuários com dados)
        df_ativo = df[df['total_views'] > 0]
        if not df_ativo.empty:
            df.loc[df['total_views'] > 0, 'rank_views'] = df_ativo['total_views'].rank(ascending=False, method='min').astype(int)
            df.loc[df['total_likes'] > 0, 'rank_likes'] = df_ativo['total_likes'].rank(ascending=False, method='min').astype(int)
            df.loc[df['taxa_engajamento'] > 0, 'rank_engajamento'] = df_ativo['taxa_engajamento'].rank(ascending=False, method='min').astype(int)
            df.loc[df['score_performance'] > 0, 'rank_performance'] = df_ativo['score_performance'].rank(ascending=False, method='min').astype(int)
        
        # Preencher NaN dos rankings com 0
        df[['rank_views', 'rank_likes', 'rank_engajamento', 'rank_performance']] = df[['rank_views', 'rank_likes', 'rank_engajamento', 'rank_performance']].fillna(0).astype(int)
        
        # Análise de consistência
        df['consistencia'] = np.where(
            df['total_videos'] > 5,
            np.where(df['taxa_engajamento'] > df['taxa_engajamento'].median(), "Alta", "Média"),
            np.where(df['total_videos'] > 0, "Baixa", "Sem dados")
        )
        
        # Status do usuário
        df['status_usuario'] = np.where(
            df['total_views'] == 0,
            "🔴 Inativo",
            np.where(
                df['total_views'] >= df['total_views'].quantile(0.75),
                "🟢 Muito Ativo",
                np.where(
                    df['total_views'] >= df['total_views'].median(),
                    "🟡 Ativo",
                    "🟠 Pouco Ativo"
                )
            )
        )
        
        # Potencial de crescimento
        df['potencial_crescimento'] = np.where(
            df['total_views'] == 0,
            "Sem dados",
            np.where(
                (df['taxa_engajamento'] > df['taxa_engajamento'].quantile(0.75)) & 
                (df['total_videos'] < df['total_videos'].quantile(0.5)),
                "Alto", 
                np.where(df['taxa_engajamento'] > df['taxa_engajamento'].median(), "Médio", "Baixo")
            )
        )
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        if conn:
            conn.close()
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def carregar_videos_completo():
    """Carrega TODOS os vídeos do banco (sem limite)"""
    conn = conectar_banco()
    if not conn:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='valid_videos'")
        if not cursor.fetchone():
            conn.close()
            return pd.DataFrame()
        
        # Primeiro, contar quantos vídeos existem
        cursor.execute("SELECT COUNT(*) FROM valid_videos")
        total_videos = cursor.fetchone()[0]
        
        # Query sem LIMIT para carregar todos
        query = """
        SELECT 
            v.*,
            cs.discord_username
        FROM valid_videos v
        LEFT JOIN cached_stats cs ON v.user_id = cs.user_id
        WHERE cs.discord_username IS NOT NULL
        ORDER BY v.id DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            # Converter colunas numéricas de forma segura
            numeric_cols = ['views', 'likes', 'comments', 'shares']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = converter_para_numerico_seguro(df[col], 0)
            
            # Métricas avançadas por vídeo usando fórmulas reais
            if 'views' in df.columns and 'likes' in df.columns:
                df['interactions'] = df['likes'] + df['comments'] + df['shares']
                
                # Taxa de engajamento usando fórmula da plataforma específica
                df['engagement_rate'] = df.apply(
                    lambda x: calcular_engajamento_por_plataforma(
                        x['views'], x['likes'], x['comments'], 
                        x['shares'], x.get('platform', 'geral')
                    ), axis=1
                )
                
                # Score do vídeo simplificado
                df['video_score'] = (
                    df['engagement_rate'] * 0.6 +  # 60% engajamento
                    np.log1p(df['views']) * 0.4     # 40% alcance
                ).round(2)
                
                # Categoria do vídeo (convertida para string)
                try:
                    df['categoria_video'] = pd.cut(
                        df['engagement_rate'],
                        bins=[0, 1, 3, 6, 10, 100],
                        labels=['🔴 Baixo', '🟡 Regular', '🟢 Bom', '🔵 Muito Bom', '🟣 Excepcional'],
                        include_lowest=True
                    ).astype(str)
                except:
                    # Fallback se pd.cut falhar
                    df['categoria_video'] = '📊 Sem categoria'
                
                # Status do link
                df['tem_link'] = df['url'].notna() & (df['url'] != '') & (df['url'].str.len() > 10)
            
            # Adicionar informação sobre o total
            st.session_state['total_videos_banco'] = total_videos
            st.session_state['videos_carregados'] = len(df)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar vídeos: {str(e)}")
        if conn:
            conn.close()
        return pd.DataFrame()

def detectar_dispositivo_mobile():
    """Detecta se o usuário está em um dispositivo móvel baseado na largura da tela"""
    # Usando JavaScript para detectar largura da tela
    return st.markdown("""
    <script>
    if (window.innerWidth <= 768) {
        document.body.classList.add('mobile-device');
    }
    </script>
    """, unsafe_allow_html=True)

def detectar_plataforma_do_link(url):
    """Detecta a plataforma baseada no URL - versão melhorada"""
    try:
        import re
    except ImportError:
        # Fallback caso re não esteja disponível
        if not url:
            return None, None
        
        url = url.lower().strip()
        
        if 'tiktok.com' in url:
            return 'tiktok', 'usuario_tiktok'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube', 'usuario_youtube'
        elif 'instagram.com' in url:
            return 'instagram', 'usuario_instagram'
        
        return None, None
    
    if not url:
        return None, None
    
    url = url.lower().strip()
    
    # Padrões para TikTok - versão melhorada
    if 'tiktok.com' in url:
        # Padrão principal: tiktok.com/@usuario/video/123
        match = re.search(r'tiktok\.com/@([^/\?&\s]+)', url)
        if match:
            username = match.group(1)
            # Limpar username de caracteres especiais
            username = re.sub(r'[^\w\-\.]', '', username)
            return 'tiktok', username
        
        # tiktok.com/t/VIDEO_ID (link curto oficial)
        match = re.search(r'tiktok\.com/t/([^/\?&\s]+)', url)
        if match:
            video_id = match.group(1)
            return 'tiktok', f"short_link_{video_id}"
        
        # Links curtos do TikTok vm.tiktok.com
        match = re.search(r'vm\.tiktok\.com/([^/\?&\s]+)', url)
        if match:
            short_id = match.group(1)
            return 'tiktok', f"vm_link_{short_id}"
        
        # m.tiktok.com (versão mobile)
        if 'm.tiktok.com' in url:
            match = re.search(r'm\.tiktok\.com.*/@([^/\?&\s]+)', url)
            if match:
                username = match.group(1)
                username = re.sub(r'[^\w\-\.]', '', username)
                return 'tiktok', username
            else:
                return 'tiktok', 'mobile_tiktok_detectado'
        
        # Extrair ID do vídeo diretamente
        match = re.search(r'/video/(\d+)', url)
        if match:
            video_id = match.group(1)
            return 'tiktok', f"video_{video_id}"
        
        # Fallback: assumir que é TikTok mesmo sem conseguir extrair username
        return 'tiktok', 'usuario_tiktok_detectado'
    
    # Padrões para YouTube - versão melhorada
    elif 'youtube.com' in url or 'youtu.be' in url:
        # youtube.com/@canal (formato novo)
        match = re.search(r'youtube\.com/@([^/\?&\s]+)', url)
        if match:
            username = match.group(1)
            username = re.sub(r'[^\w\-\.]', '', username)
            return 'youtube', username
        
        # youtube.com/c/canal (formato antigo)
        match = re.search(r'youtube\.com/c/([^/\?&\s]+)', url)
        if match:
            username = match.group(1)
            username = re.sub(r'[^\w\-\.]', '', username)
            return 'youtube', username
        
        # youtube.com/channel/ID
        match = re.search(r'youtube\.com/channel/([^/\?&\s]+)', url)
        if match:
            channel_id = match.group(1)
            return 'youtube', f"channel_{channel_id[:15]}"
        
        # youtube.com/user/usuario
        match = re.search(r'youtube\.com/user/([^/\?&\s]+)', url)
        if match:
            username = match.group(1)
            username = re.sub(r'[^\w\-\.]', '', username)
            return 'youtube', username
        
        # youtube.com/shorts/VIDEO_ID (YouTube Shorts)
        if 'youtube.com/shorts/' in url:
            match = re.search(r'youtube\.com/shorts/([^/\?&\s]+)', url)
            if match:
                video_id = match.group(1)
                # Para Shorts, retornar o ID do vídeo para busca posterior
                return 'youtube', f"shorts_{video_id[:11]}"  # YouTube video IDs são 11 caracteres
        
        # Fallback: assumir que é YouTube mesmo sem conseguir extrair canal específico
        return 'youtube', 'canal_youtube_detectado'
    
    # Padrões para Instagram - versão melhorada
    elif 'instagram.com' in url:
        # instagram.com/p/POST_ID (post)
        if 'instagram.com/p/' in url:
            match = re.search(r'instagram\.com/p/([^/\?&\s]+)', url)
            if match:
                post_id = match.group(1)
                return 'instagram', f"post_{post_id}"
        
        # instagram.com/reel/REEL_ID (reel)
        elif 'instagram.com/reel/' in url:
            match = re.search(r'instagram\.com/reel/([^/\?&\s]+)', url)
            if match:
                reel_id = match.group(1)
                return 'instagram', f"reel_{reel_id}"
        
        # instagram.com/tv/TV_ID (IGTV)
        elif 'instagram.com/tv/' in url:
            match = re.search(r'instagram\.com/tv/([^/\?&\s]+)', url)
            if match:
                tv_id = match.group(1)
                return 'instagram', f"igtv_{tv_id}"
        
        # instagram.com/stories/USUARIO/STORY_ID (stories)
        elif 'instagram.com/stories/' in url:
            match = re.search(r'instagram\.com/stories/([^/\?&\s]+)', url)
            if match:
                username = match.group(1)
                username = re.sub(r'[^\w\-\.]', '', username)
                return 'instagram', f"story_{username}"
        
        # instagram.com/usuario/ (perfil)
        else:
            match = re.search(r'instagram\.com/([^/\?&\s]+)/?(?:$|\?)', url)
            if match:
                username = match.group(1)
                # Filtrar se não é uma página especial
                if username not in ['p', 'reel', 'tv', 'stories', 'explore', 'accounts', 'direct', 'about']:
                    username = re.sub(r'[^\w\-\.]', '', username)
                    return 'instagram', username
        
        # Fallback
        return 'instagram', 'usuario_instagram_detectado'
    
    return None, None

def obter_contas_por_usuario_melhorado(df_usuarios, df_videos):
    """Versão melhorada que detecta contas de forma mais robusta"""
    if df_usuarios.empty:
        return []
    
    contas_usuarios = []
    
    # Debug: contar quantos vídeos têm URLs
    videos_com_url = 0
    if not df_videos.empty and 'url' in df_videos.columns:
        videos_com_url = len(df_videos[df_videos['url'].notna()])
    
    for _, usuario in df_usuarios.iterrows():
        username_discord = usuario['discord_username']
        
        # Inicializar conjuntos de contas
        contas_tiktok = set()
        contas_youtube = set()
        contas_instagram = set()
        
        # Método 1: Analisar URLs dos vídeos deste usuário
        if not df_videos.empty and 'discord_username' in df_videos.columns:
            videos_usuario = df_videos[df_videos['discord_username'] == username_discord]
            
            for _, video in videos_usuario.iterrows():
                if pd.notna(video.get('url')):
                    url = str(video['url']).strip()
                    if url:
                        plataforma, username = detectar_plataforma_do_link(url)
                        
                        if plataforma and username:
                            # Filtrar usernames genéricos ou IDs de posts/vídeos
                            if not any(x in username.lower() for x in ['video_especifico', 'detectado', 'link_curto', 'post_', 'reel_', 'channel_', 'shorts_', 'video_', 'vm_link_', 'short_link_', 'igtv_', 'story_']):
                                if plataforma == 'tiktok' and len(username) > 2:
                                    contas_tiktok.add(username)
                                elif plataforma == 'youtube' and len(username) > 2:
                                    contas_youtube.add(username)
                                elif plataforma == 'instagram' and len(username) > 2:
                                    contas_instagram.add(username)
                            # Para formatos especiais, ainda considerar como atividade na plataforma
                            else:
                                if plataforma == 'tiktok':
                                    contas_tiktok.add('conta_tiktok_ativa')
                                elif plataforma == 'youtube' and 'shorts_' in username.lower():
                                    contas_youtube.add('canal_youtube_shorts')
                                elif plataforma == 'instagram':
                                    contas_instagram.add('conta_instagram_ativa')
        
        # Método 2: Buscar por similaridade de nomes (fallback)
        if not (contas_tiktok or contas_youtube or contas_instagram):
            # Se não encontrou nada, vamos buscar de forma mais ampla
            username_parts = username_discord.lower().replace('#', '').replace(' ', '')
            
            # Buscar em todos os vídeos por similaridade
            if not df_videos.empty and 'url' in df_videos.columns:
                for _, video in df_videos.iterrows():
                    if pd.notna(video.get('url')):
                        url = str(video['url']).lower()
                        
                        # Se o username ou parte dele aparece na URL
                        if username_parts in url or any(part in url for part in username_parts.split('_') if len(part) > 3):
                            plataforma, username_url = detectar_plataforma_do_link(video['url'])
                            
                            if plataforma == 'tiktok':
                                contas_tiktok.add(username_url or 'conta_detectada')
                            elif plataforma == 'youtube':
                                contas_youtube.add(username_url or 'conta_detectada')
                            elif plataforma == 'instagram':
                                contas_instagram.add(username_url or 'conta_detectada')
        
        # Método 3: Verificar se tem vídeos nas plataformas mas não detectou conta
        # Se tem vídeos na plataforma, mas não detectou conta, adicionar genérico
        if usuario.get('tiktok_videos', 0) > 0 and not contas_tiktok:
            contas_tiktok.add(f"@{username_discord.split('#')[0].lower()}")
        
        if usuario.get('youtube_videos', 0) > 0 and not contas_youtube:
            contas_youtube.add(f"@{username_discord.split('#')[0].lower()}")
        
        if usuario.get('instagram_videos', 0) > 0 and not contas_instagram:
            contas_instagram.add(f"@{username_discord.split('#')[0].lower()}")
        
        # Compilar informações do usuário
        user_info = {
            'discord_username': username_discord,
            'total_videos': usuario.get('total_videos', 0),
            'total_views': usuario.get('total_views', 0),
            'contas_tiktok': list(contas_tiktok),
            'contas_youtube': list(contas_youtube),
            'contas_instagram': list(contas_instagram),
            'videos_tiktok': usuario.get('tiktok_videos', 0),
            'videos_youtube': usuario.get('youtube_videos', 0),
            'videos_instagram': usuario.get('instagram_videos', 0),
            'views_tiktok': usuario.get('tiktok_views', 0),
            'views_youtube': usuario.get('youtube_views', 0),
            'views_instagram': usuario.get('instagram_views', 0)
        }
        
        # Determinar status de completude
        plataformas_ativas = 0
        plataformas_com_videos = 0
        
        if user_info['videos_tiktok'] > 0:
            plataformas_com_videos += 1
            if user_info['contas_tiktok']:
                plataformas_ativas += 1
        
        if user_info['videos_youtube'] > 0:
            plataformas_com_videos += 1
            if user_info['contas_youtube']:
                plataformas_ativas += 1
        
        if user_info['videos_instagram'] > 0:
            plataformas_com_videos += 1
            if user_info['contas_instagram']:
                plataformas_ativas += 1
        
        # Status baseado em contas detectadas vs vídeos existentes
        if plataformas_com_videos == 0:
            user_info['status'] = "😴 Inativo"
        elif plataformas_ativas == plataformas_com_videos and plataformas_com_videos >= 2:
            user_info['status'] = "🟢 Completo"
        elif plataformas_ativas > 0:
            user_info['status'] = "🟡 Parcial"
        else:
            user_info['status'] = "🔴 Sem contas detectadas"
        
        user_info['plataformas_ativas'] = plataformas_ativas
        user_info['plataformas_com_videos'] = plataformas_com_videos
        
        # Debug info
        user_info['debug_info'] = {
            'videos_analisados': len(df_videos[df_videos.get('discord_username') == username_discord]) if not df_videos.empty else 0,
            'urls_validas': len([v for v in df_videos[df_videos.get('discord_username') == username_discord]['url'].dropna() if str(v).strip()]) if not df_videos.empty and 'discord_username' in df_videos.columns else 0
        }
        
        contas_usuarios.append(user_info)
    
    # Ordenar por número de plataformas ativas (decrescente) e depois por views
    contas_usuarios.sort(key=lambda x: (x['plataformas_ativas'], x['total_views']), reverse=True)
    
    return contas_usuarios

def buscar_video_no_banco(url, df_videos):
    """Busca se o vídeo existe no banco de dados - versão melhorada"""
    if df_videos.empty or 'url' not in df_videos.columns:
        return None
    
    # Busca exata primeiro
    video_exato = df_videos[df_videos['url'] == url]
    if not video_exato.empty:
        return video_exato.iloc[0]
    
    # Extrair ID do vídeo para comparação mais inteligente
    import re
    
    # Para YouTube: extrair video ID
    youtube_id = None
    if 'youtube.com' in url or 'youtu.be' in url:
        # youtube.com/watch?v=ID
        match = re.search(r'[?&]v=([^&]+)', url)
        if match:
            youtube_id = match.group(1)
        # youtu.be/ID
        elif 'youtu.be/' in url:
            match = re.search(r'youtu\.be/([^?&]+)', url)
            if match:
                youtube_id = match.group(1)
        # youtube.com/shorts/ID
        elif 'youtube.com/shorts/' in url:
            match = re.search(r'youtube\.com/shorts/([^?&]+)', url)
            if match:
                youtube_id = match.group(1)
    
    # Para TikTok: extrair video ID
    tiktok_id = None
    if 'tiktok.com' in url:
        # Extrair ID do vídeo: /video/123456
        match = re.search(r'/video/(\d+)', url)
        if match:
            tiktok_id = match.group(1)
        # Links curtos tiktok.com/t/
        elif '/t/' in url:
            match = re.search(r'/t/([^/?&]+)', url)
            if match:
                tiktok_id = match.group(1)
        # Links vm.tiktok.com
        elif 'vm.tiktok.com' in url:
            match = re.search(r'vm\.tiktok\.com/([^/?&]+)', url)
            if match:
                tiktok_id = match.group(1)
    
    # Para Instagram: extrair post/reel ID
    instagram_id = None
    if 'instagram.com' in url:
        if '/p/' in url:
            match = re.search(r'/p/([^/?&]+)', url)
            if match:
                instagram_id = match.group(1)
        elif '/reel/' in url:
            match = re.search(r'/reel/([^/?&]+)', url)
            if match:
                instagram_id = match.group(1)
        elif '/tv/' in url:
            match = re.search(r'/tv/([^/?&]+)', url)
            if match:
                instagram_id = match.group(1)
    
    # Buscar por IDs extraídos
    for _, video in df_videos.iterrows():
        if pd.notna(video['url']):
            video_url = str(video['url'])
            
            # Comparar IDs do YouTube
            if youtube_id:
                if youtube_id in video_url:
                    return video
                # Verificar diferentes formatos do mesmo vídeo
                video_youtube_id = None
                if 'youtube.com' in video_url or 'youtu.be' in video_url:
                    match = re.search(r'[?&]v=([^&]+)', video_url)
                    if match:
                        video_youtube_id = match.group(1)
                    elif 'youtu.be/' in video_url:
                        match = re.search(r'youtu\.be/([^?&]+)', video_url)
                        if match:
                            video_youtube_id = match.group(1)
                    elif 'youtube.com/shorts/' in video_url:
                        match = re.search(r'youtube\.com/shorts/([^?&]+)', video_url)
                        if match:
                            video_youtube_id = match.group(1)
                    
                    if video_youtube_id == youtube_id:
                        return video
            
            # Comparar IDs do TikTok
            elif tiktok_id:
                if tiktok_id in video_url:
                    return video
                # Verificar diferentes formatos do mesmo vídeo TikTok
                video_tiktok_id = None
                if 'tiktok.com' in video_url:
                    # /video/ID
                    match = re.search(r'/video/(\d+)', video_url)
                    if match:
                        video_tiktok_id = match.group(1)
                    # /t/ID
                    elif '/t/' in video_url:
                        match = re.search(r'/t/([^/?&]+)', video_url)
                        if match:
                            video_tiktok_id = match.group(1)
                    # vm.tiktok.com
                    elif 'vm.tiktok.com' in video_url:
                        match = re.search(r'vm\.tiktok\.com/([^/?&]+)', video_url)
                        if match:
                            video_tiktok_id = match.group(1)
                    
                    if video_tiktok_id == tiktok_id:
                        return video
            
            # Comparar IDs do Instagram
            elif instagram_id:
                if instagram_id in video_url:
                    return video
                # Verificar diferentes formatos do mesmo post/reel/IGTV
                video_instagram_id = None
                if 'instagram.com' in video_url:
                    if '/p/' in video_url:
                        match = re.search(r'/p/([^/?&]+)', video_url)
                        if match:
                            video_instagram_id = match.group(1)
                    elif '/reel/' in video_url:
                        match = re.search(r'/reel/([^/?&]+)', video_url)
                        if match:
                            video_instagram_id = match.group(1)
                    elif '/tv/' in video_url:
                        match = re.search(r'/tv/([^/?&]+)', video_url)
                        if match:
                            video_instagram_id = match.group(1)
                    
                    if video_instagram_id == instagram_id:
                        return video
    
    # Busca parcial (para casos de links com parâmetros diferentes)
    url_limpo = url.split('?')[0]  # Remove parâmetros
    
    for _, video in df_videos.iterrows():
        if pd.notna(video['url']):
            video_url_limpo = str(video['url']).split('?')[0]
            if url_limpo in video_url_limpo or video_url_limpo in url_limpo:
                return video
    
    return None

def identificar_dono_da_conta(plataforma, username, df_usuarios, video_info=None):
    """Identifica qual usuário Discord é dono da conta - versão melhorada"""
    
    # Prioridade 1: Se o vídeo tem criador conhecido, usar essa informação
    if video_info is not None and 'discord_username' in video_info.index and pd.notna(video_info['discord_username']):
        # Buscar usuário completo baseado no discord_username do vídeo
        usuario_encontrado = df_usuarios[df_usuarios['discord_username'] == video_info['discord_username']]
        if not usuario_encontrado.empty:
            return usuario_encontrado.iloc[0]
    
    # Prioridade 2: Busca por username se fornecido
    if not plataforma or not username or df_usuarios.empty:
        return None
    
    coluna_plataforma = f"{plataforma.lower()}_username"
    
    # Se existe coluna específica da plataforma
    if coluna_plataforma in df_usuarios.columns:
        dono = df_usuarios[df_usuarios[coluna_plataforma].str.contains(username, case=False, na=False)]
        if not dono.empty:
            return dono.iloc[0]
    
    # Busca em outras colunas que possam conter o username
    colunas_busca = ['discord_username', 'user_id']
    for coluna in colunas_busca:
        if coluna in df_usuarios.columns:
            dono = df_usuarios[df_usuarios[coluna].str.contains(username, case=False, na=False)]
            if not dono.empty:
                return dono.iloc[0]
    
    return None

def extrair_informacoes_do_link(url, df_videos, df_usuarios):
    """Função principal que extrai todas as informações de um link"""
    if not url.strip():
        return None
    
    # 1. Detectar plataforma e extrair username
    plataforma, username = detectar_plataforma_do_link(url)
    
    # 2. Buscar vídeo no banco
    video_info = buscar_video_no_banco(url, df_videos)
    
    # 3. Identificar dono da conta (priorizar info do vídeo se encontrado)
    dono_conta = identificar_dono_da_conta(plataforma, username, df_usuarios, video_info)
    
    # 4. Compilar informações
    resultado = {
        'url_original': url,
        'plataforma': plataforma,
        'username_extraido': username,
        'video_cadastrado': video_info is not None,
        'video_info': video_info,
        'dono_identificado': dono_conta is not None,
        'dono_info': dono_conta,
        'status': 'sucesso' if plataforma else 'erro'
    }
    
    return resultado

def obter_contas_por_usuario(df_usuarios, df_videos):
    """Obtém lista de contas por usuário baseada nos vídeos cadastrados"""
    if df_usuarios.empty or df_videos.empty:
        return []
    
    contas_usuarios = []
    
    for _, usuario in df_usuarios.iterrows():
        # Vídeos deste usuário
        videos_usuario = df_videos[df_videos.get('discord_username') == usuario['discord_username']]
        
        # Contas detectadas pelos vídeos
        contas_tiktok = set()
        contas_youtube = set()
        contas_instagram = set()
        
        for _, video in videos_usuario.iterrows():
            if pd.notna(video.get('url')):
                plataforma, username = detectar_plataforma_do_link(video['url'])
                if plataforma and username and not username.startswith(('video_especifico', 'post_', 'reel_', 'link_curto_')):
                    if plataforma == 'tiktok':
                        contas_tiktok.add(username)
                    elif plataforma == 'youtube':
                        contas_youtube.add(username)
                    elif plataforma == 'instagram':
                        contas_instagram.add(username)
        
        # Compilar informações do usuário
        user_info = {
            'discord_username': usuario['discord_username'],
            'total_videos': usuario.get('total_videos', 0),
            'total_views': usuario.get('total_views', 0),
            'contas_tiktok': list(contas_tiktok),
            'contas_youtube': list(contas_youtube),
            'contas_instagram': list(contas_instagram),
            'videos_tiktok': usuario.get('tiktok_videos', 0),
            'videos_youtube': usuario.get('youtube_videos', 0),
            'videos_instagram': usuario.get('instagram_videos', 0),
            'views_tiktok': usuario.get('tiktok_views', 0),
            'views_youtube': usuario.get('youtube_views', 0),
            'views_instagram': usuario.get('instagram_views', 0)
        }
        
        # Determinar status de completude
        plataformas_ativas = 0
        if user_info['contas_tiktok']:
            plataformas_ativas += 1
        if user_info['contas_youtube']:
            plataformas_ativas += 1
        if user_info['contas_instagram']:
            plataformas_ativas += 1
        
        if plataformas_ativas == 3:
            user_info['status'] = "🟢 Completo"
        elif plataformas_ativas >= 1:
            user_info['status'] = "🟡 Parcial"
        else:
            user_info['status'] = "🔴 Sem contas"
        
        user_info['plataformas_ativas'] = plataformas_ativas
        
        contas_usuarios.append(user_info)
    
    # Ordenar por número de plataformas ativas (decrescente) e depois por views
    contas_usuarios.sort(key=lambda x: (x['plataformas_ativas'], x['total_views']), reverse=True)
    
    return contas_usuarios

def pagina_gestao_contas(df_videos, df_usuarios):
    """Nova página para gestão de contas e identificação"""
    st.markdown('<div class="main-header"><h1>🔗 Gestão de Contas e Identificação</h1><p>Identifique donos de links e gerencie contas dos usuários</p></div>', unsafe_allow_html=True)
    
    if df_videos.empty and df_usuarios.empty:
        st.error("❌ Nenhum dado disponível para gestão de contas")
        return
    
    # Estatísticas gerais da gestão
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        videos_com_link = len(df_videos[df_videos.get('url', pd.Series()).notna()]) if not df_videos.empty else 0
        st.metric("🔗 Vídeos com Links", f"{videos_com_link:,}")
    
    with col2:
        usuarios_ativos = len(df_usuarios[df_usuarios.get('total_views', 0) > 0]) if not df_usuarios.empty else 0
        st.metric("👥 Usuários Ativos", f"{usuarios_ativos:,}")
    
    with col3:
        # Contar plataformas detectadas
        plataformas_detectadas = set()
        if not df_videos.empty and 'url' in df_videos.columns:
            for url in df_videos['url'].dropna():
                plataforma, _ = detectar_plataforma_do_link(str(url))
                if plataforma:
                    plataformas_detectadas.add(plataforma)
        st.metric("📱 Plataformas", len(plataformas_detectadas))
    
    with col4:
        # Contas únicas detectadas
        contas_unicas = set()
        if not df_videos.empty and 'url' in df_videos.columns:
            for url in df_videos['url'].dropna():
                _, username = detectar_plataforma_do_link(str(url))
                if username and not username.startswith(('video_especifico', 'post_', 'reel_', 'link_curto_')):
                    contas_unicas.add(username)
        st.metric("🎯 Contas Detectadas", len(contas_unicas))
    
    st.divider()
    
    # Abas principais
    tab1, tab2 = st.tabs(["🔍 Identificar Link", "👥 Contas dos Usuários"])
    
    with tab1:
        st.subheader("🔍 Identificador de Links de Vídeos")
        st.info("💡 Cole um link de vídeo para descobrir automaticamente a plataforma e o dono")
        
        # Interface de identificação
        col1, col2 = st.columns([3, 1])
        
        with col1:
            url_input = st.text_input(
                "🔗 Cole o link do vídeo aqui:",
                placeholder="Ex: tiktok.com/t/abc, youtube.com/shorts/xyz, instagram.com/reel/123",
                help="Suporta TODOS os formatos: TikTok (5 tipos), YouTube (6 tipos), Instagram (6 tipos) - Total: 17 formatos!"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento
            analisar = st.button("🔍 Analisar Link", type="primary", use_container_width=True)
        
        # Análise do link
        if url_input and analisar:
            with st.spinner("🔄 Analisando link..."):
                resultado = extrair_informacoes_do_link(url_input, df_videos, df_usuarios)
                
                if resultado['status'] == 'erro':
                    st.error("❌ Link não reconhecido ou formato inválido")
                    st.info("💡 **Formatos suportados (17 tipos):**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info("**🎵 TikTok:**\n• @usuario/video/123\n• /t/abc123\n• vm.tiktok.com\n• m.tiktok.com\n• @usuario")
                    with col2:
                        st.info("**📺 YouTube:**\n• /watch?v=abc\n• /shorts/abc\n• /@canal\n• /c/canal\n• youtu.be/abc")
                    with col3:
                        st.info("**📸 Instagram:**\n• /p/abc123\n• /reel/xyz\n• /tv/def\n• /stories/user\n• /usuario")
                else:
                    # Mostrar resultados
                    st.success("✅ Link analisado com sucesso!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Informações da plataforma
                        plataforma_emoji = {
                            'tiktok': '🎵',
                            'youtube': '📺', 
                            'instagram': '📸'
                        }.get(resultado['plataforma'], '📱')
                        
                        # Detectar tipo de conteúdo específico
                        tipo_conteudo = ""
                        username_display = resultado['username_extraido']
                        
                        if resultado['plataforma'] == 'youtube':
                            if 'shorts_' in username_display:
                                tipo_conteudo = " (YouTube Short)"
                                plataforma_emoji = "🩳"
                                video_id = username_display.replace('shorts_', '')
                                username_display = f"Short ID: {video_id}"
                            elif 'canal_' in username_display:
                                tipo_conteudo = " (Canal)"
                                username_display = "Canal detectado"
                        
                        elif resultado['plataforma'] == 'tiktok':
                            if 'video_' in username_display:
                                tipo_conteudo = " (Vídeo)"
                                video_id = username_display.replace('video_', '')
                                username_display = f"Vídeo ID: {video_id}"
                            elif 'vm_link_' in username_display:
                                tipo_conteudo = " (Link Curto VM)"
                                plataforma_emoji = "🔗"
                                short_id = username_display.replace('vm_link_', '')
                                username_display = f"VM ID: {short_id}"
                            elif 'short_link_' in username_display:
                                tipo_conteudo = " (Link Curto T)"
                                plataforma_emoji = "🔗"
                                short_id = username_display.replace('short_link_', '')
                                username_display = f"T ID: {short_id}"
                            else:
                                username_display = f"@{username_display}"
                        
                        elif resultado['plataforma'] == 'instagram':
                            if 'post_' in username_display:
                                tipo_conteudo = " (Post)"
                                plataforma_emoji = "📷"
                                post_id = username_display.replace('post_', '')
                                username_display = f"Post ID: {post_id}"
                            elif 'reel_' in username_display:
                                tipo_conteudo = " (Reel)"
                                plataforma_emoji = "🎬"
                                reel_id = username_display.replace('reel_', '')
                                username_display = f"Reel ID: {reel_id}"
                            elif 'igtv_' in username_display:
                                tipo_conteudo = " (IGTV)"
                                plataforma_emoji = "📺"
                                tv_id = username_display.replace('igtv_', '')
                                username_display = f"IGTV ID: {tv_id}"
                            elif 'story_' in username_display:
                                tipo_conteudo = " (Story)"
                                plataforma_emoji = "📱"
                                story_user = username_display.replace('story_', '')
                                username_display = f"Story de: @{story_user}"
                            else:
                                username_display = f"@{username_display}"
                        
                        st.markdown(f"""
                        <div class="ranking-card">
                            <h4>{plataforma_emoji} Informações da Plataforma</h4>
                            <p><strong>Plataforma:</strong> {resultado['plataforma'].title()}{tipo_conteudo}</p>
                            <p><strong>Identificação:</strong> {username_display}</p>
                            <p><strong>Link analisado:</strong> <a href="{resultado['url_original']}" target="_blank">Ver original</a></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Status no banco de dados
                        if resultado['video_cadastrado']:
                            video = resultado['video_info']
                            st.markdown(f"""
                            <div class="success-box">
                                <h4>✅ Vídeo Cadastrado na Competição</h4>
                                <p><strong>Criador:</strong> {video.get('discord_username', 'N/A')}</p>
                                <p><strong>Views:</strong> {formatar_numero(video.get('views', 0))}</p>
                                <p><strong>Curtidas:</strong> {formatar_numero(video.get('likes', 0))}</p>
                                <p><strong>Plataforma:</strong> {video.get('platform', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="warning-box">
                                <h4>🚫 Vídeo NÃO cadastrado na competição</h4>
                                <p>Este vídeo não foi encontrado na base de dados da competição.</p>
                                <ul>
                                    <li>Pode ser de um usuário não participante</li>
                                    <li>Pode ser um vídeo muito recente</li>
                                    <li>Link pode ter sido alterado</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Informações do dono da conta
                    if resultado['dono_identificado']:
                        st.divider()
                        dono = resultado['dono_info']
                        
                        st.markdown("#### 👤 Dono da Conta Identificado")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="insight-box">
                                <h5>🎯 Usuário Discord</h5>
                                <p><strong>{dono['discord_username']}</strong></p>
                                <p>ID: {dono.get('user_id', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="insight-box">
                                <h5>📊 Estatísticas Gerais</h5>
                                <p><strong>Vídeos:</strong> {dono.get('total_videos', 0)}</p>
                                <p><strong>Views:</strong> {formatar_numero(dono.get('total_views', 0))}</p>
                                <p><strong>Curtidas:</strong> {formatar_numero(dono.get('total_likes', 0))}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="insight-box">
                                <h5>🏆 Performance</h5>
                                <p><strong>Score:</strong> {dono.get('score_performance', 0):.1f}/100</p>
                                <p><strong>Engajamento:</strong> {dono.get('taxa_engajamento', 0):.1f}%</p>
                                <p><strong>Categoria:</strong> {dono.get('categoria_performance', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.divider()
                        st.markdown("""
                        <div class="warning-box">
                            <h4>❓ Dono da Conta Não Identificado</h4>
                            <p>Não foi possível associar esta conta a nenhum usuário Discord cadastrado.</p>
                            <ul>
                                <li>Pode ser um criador externo</li>
                                <li>Username pode ter mudado</li>
                                <li>Associação manual pode ser necessária</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("👥 Gestão de Contas dos Usuários")
        st.info("💡 Visualize e gerencie todas as contas associadas aos usuários da competição")
        
        # Obter dados das contas
        with st.spinner("🔄 Analisando contas dos usuários..."):
            contas_usuarios = obter_contas_por_usuario_melhorado(df_usuarios, df_videos)
        
        if not contas_usuarios:
            st.warning("⚠️ Nenhuma conta foi detectada nos dados disponíveis")
            return
        
        # Debug info
        with st.expander("🔍 Informações de Debug", expanded=False):
            videos_totais = len(df_videos) if not df_videos.empty else 0
            videos_com_url = len(df_videos[df_videos['url'].notna()]) if not df_videos.empty and 'url' in df_videos.columns else 0
            usuarios_com_videos = len([u for u in contas_usuarios if u['total_videos'] > 0])
            usuarios_com_contas = len([u for u in contas_usuarios if u['plataformas_ativas'] > 0])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Vídeos no Banco", videos_totais)
            with col2:
                st.metric("🔗 Vídeos com URLs", videos_com_url)
            with col3:
                st.metric("👥 Usuários com Vídeos", usuarios_com_videos)
            with col4:
                st.metric("🎯 Usuários com Contas", usuarios_com_contas)
            
            st.info("💡 Se um usuário tem vídeos mas não tem contas detectadas, pode ser problema na extração de username dos URLs")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_status = st.selectbox(
                "🎯 Filtrar por status:",
                ["Todos", "🟢 Completo", "🟡 Parcial", "🔴 Sem contas"]
            )
        
        with col2:
            filtro_plataforma = st.selectbox(
                "📱 Filtrar por plataforma:",
                ["Todas", "TikTok", "YouTube", "Instagram"]
            )
        
        with col3:
            ordenar_por = st.selectbox(
                "📊 Ordenar por:",
                ["Plataformas ativas", "Views totais", "Vídeos totais", "Nome"]
            )
        
        # Aplicar filtros
        contas_filtradas = contas_usuarios.copy()
        
        if filtro_status != "Todos":
            contas_filtradas = [u for u in contas_filtradas if u['status'] == filtro_status]
        
        if filtro_plataforma != "Todas":
            plat_key = f"contas_{filtro_plataforma.lower()}"
            contas_filtradas = [u for u in contas_filtradas if u.get(plat_key, [])]
        
        # Ordenar
        if ordenar_por == "Views totais":
            contas_filtradas.sort(key=lambda x: x['total_views'], reverse=True)
        elif ordenar_por == "Vídeos totais":
            contas_filtradas.sort(key=lambda x: x['total_videos'], reverse=True)
        elif ordenar_por == "Nome":
            contas_filtradas.sort(key=lambda x: x['discord_username'])
        
        st.info(f"📊 Mostrando {len(contas_filtradas)} de {len(contas_usuarios)} usuários")
        
        # Exibir contas
        for i, usuario in enumerate(contas_filtradas):
            debug_info = usuario.get('debug_info', {})
            videos_analisados = debug_info.get('videos_analisados', 0)
            urls_validas = debug_info.get('urls_validas', 0)
            
            status_debug = ""
            if videos_analisados > 0 and usuario['plataformas_ativas'] == 0:
                status_debug = f" ⚠️ {videos_analisados} vídeos analisados, {urls_validas} URLs válidas"
            
            with st.expander(f"{usuario['status']} {usuario['discord_username']} ({usuario['plataformas_ativas']}/{usuario['plataformas_com_videos']} plataformas){status_debug}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Informações das contas
                    st.markdown("#### 📱 Contas por Plataforma")
                    
                    plataforma_cols = st.columns(3)
                    
                    # TikTok
                    with plataforma_cols[0]:
                        if usuario['contas_tiktok']:
                            contas_display = "<br>".join([f"@{conta}" for conta in usuario['contas_tiktok']])
                            st.markdown(f"""
                            <div class="success-box">
                                <h5>🎵 TikTok ({len(usuario['contas_tiktok'])})</h5>
                                {contas_display}
                                <br><small>{usuario['videos_tiktok']} vídeos • {formatar_numero(usuario['views_tiktok'])} views</small>
                            </div>
                            """, unsafe_allow_html=True)
                        elif usuario['videos_tiktok'] > 0:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h5>🎵 TikTok</h5>
                                <small>❌ {usuario['videos_tiktok']} vídeos, mas conta não detectada</small><br>
                                <small>🔍 URLs podem ter formato inesperado</small>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="stats-box">
                                <h5>🎵 TikTok</h5>
                                <small>Nenhum vídeo nesta plataforma</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # YouTube
                    with plataforma_cols[1]:
                        if usuario['contas_youtube']:
                            contas_display = "<br>".join([f"@{conta}" for conta in usuario['contas_youtube']])
                            st.markdown(f"""
                            <div class="success-box">
                                <h5>📺 YouTube ({len(usuario['contas_youtube'])})</h5>
                                {contas_display}
                                <br><small>{usuario['videos_youtube']} vídeos • {formatar_numero(usuario['views_youtube'])} views</small>
                            </div>
                            """, unsafe_allow_html=True)
                        elif usuario['videos_youtube'] > 0:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h5>📺 YouTube</h5>
                                <small>❌ {usuario['videos_youtube']} vídeos, mas conta não detectada</small><br>
                                <small>🔍 URLs podem ter formato inesperado</small>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="stats-box">
                                <h5>📺 YouTube</h5>
                                <small>Nenhum vídeo nesta plataforma</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Instagram
                    with plataforma_cols[2]:
                        if usuario['contas_instagram']:
                            contas_display = "<br>".join([f"@{conta}" for conta in usuario['contas_instagram']])
                            st.markdown(f"""
                            <div class="success-box">
                                <h5>📸 Instagram ({len(usuario['contas_instagram'])})</h5>
                                {contas_display}
                                <br><small>{usuario['videos_instagram']} vídeos • {formatar_numero(usuario['views_instagram'])} views</small>
                            </div>
                            """, unsafe_allow_html=True)
                        elif usuario['videos_instagram'] > 0:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h5>📸 Instagram</h5>
                                <small>❌ {usuario['videos_instagram']} vídeos, mas conta não detectada</small><br>
                                <small>🔍 URLs podem ter formato inesperado</small>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="stats-box">
                                <h5>📸 Instagram</h5>
                                <small>Nenhum vídeo nesta plataforma</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Debug detalhado para casos problemáticos
                    if videos_analisados > 0 and usuario['plataformas_ativas'] == 0:
                        st.markdown("#### 🔍 Debug Detalhado")
                        st.warning(f"⚠️ Este usuário tem {videos_analisados} vídeos, mas nenhuma conta foi detectada automaticamente.")
                        
                        # Mostrar alguns URLs para debug
                        if not df_videos.empty and 'discord_username' in df_videos.columns:
                            videos_usuario = df_videos[df_videos['discord_username'] == usuario['discord_username']]
                            urls_amostra = videos_usuario['url'].dropna().head(3).tolist()
                            
                            if urls_amostra:
                                st.markdown("**Exemplos de URLs encontradas:**")
                                for j, url in enumerate(urls_amostra, 1):
                                    plataforma, username = detectar_plataforma_do_link(url)
                                    st.code(f"{j}. {url[:60]}... → {plataforma or 'NÃO DETECTADA'} / {username or 'SEM USERNAME'}")
                
                with col2:
                    # Estatísticas do usuário
                    st.markdown("#### 📊 Estatísticas Gerais")
                    
                    st.metric("🎥 Total de Vídeos", usuario['total_videos'])
                    st.metric("👁️ Total de Views", formatar_numero(usuario['total_views']))
                    st.metric("🔍 Vídeos Analisados", videos_analisados)
                    st.metric("🔗 URLs Válidas", urls_validas)
                    
                    # Status de detecção
                    if usuario['plataformas_ativas'] > 0:
                        st.success(f"✅ {usuario['plataformas_ativas']} plataformas detectadas")
                    elif usuario['total_videos'] > 0:
                        st.error(f"❌ {usuario['total_videos']} vídeos, mas 0 contas detectadas")
                    else:
                        st.info("😴 Usuário sem vídeos")
                    
                    # Distribuição por plataforma
                    if usuario['total_videos'] > 0:
                        st.markdown("**📈 Distribuição:**")
                        
                        for plataforma, videos, views in [
                            ('TikTok', usuario['videos_tiktok'], usuario['views_tiktok']),
                            ('YouTube', usuario['videos_youtube'], usuario['views_youtube']),
                            ('Instagram', usuario['videos_instagram'], usuario['views_instagram'])
                        ]:
                            if videos > 0:
                                perc_videos = (videos / usuario['total_videos']) * 100
                                perc_views = (views / usuario['total_views']) * 100 if usuario['total_views'] > 0 else 0
                                st.markdown(f"• **{plataforma}:** {videos} vídeos ({perc_videos:.1f}%) • {formatar_numero(views)} views ({perc_views:.1f}%)")
        
        # Botão para forçar re-análise
        st.divider()
        if st.button("🔄 Forçar Re-análise das Contas", help="Executa novamente a detecção de contas"):
            st.cache_data.clear()
            st.rerun()
        
        # Estatísticas de resumo
        st.divider()
        st.markdown("#### 📈 Resumo das Contas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            usuarios_completos = len([u for u in contas_usuarios if u['plataformas_ativas'] == 3])
            st.metric("🟢 Usuários Completos", f"{usuarios_completos}", 
                     help="Usuários com contas em todas as 3 plataformas")
        
        with col2:
            usuarios_parciais = len([u for u in contas_usuarios if 1 <= u['plataformas_ativas'] < 3])
            st.metric("🟡 Usuários Parciais", f"{usuarios_parciais}",
                     help="Usuários com contas em 1-2 plataformas")
        
        with col3:
            usuarios_sem_contas = len([u for u in contas_usuarios if u['plataformas_ativas'] == 0])
            st.metric("🔴 Sem Contas", f"{usuarios_sem_contas}",
                     help="Usuários sem contas detectadas")
        
        with col4:
            total_contas_detectadas = sum(len(u['contas_tiktok']) + len(u['contas_youtube']) + len(u['contas_instagram']) for u in contas_usuarios)
            st.metric("🎯 Total de Contas", f"{total_contas_detectadas}",
                     help="Total de contas únicas detectadas")

def criar_ranking_card(titulo, subtitulo, cor_bg, usuarios_data, metrica_principal, metrica_secundaria, icone_metrica):
    """Cria um card de ranking padronizado"""
    st.markdown(f"""
    <div style="background: {cor_bg}; 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;">
        <h4 style="margin: 0; color: white;">{titulo}</h4>
        <small style="color: rgba(255,255,255,0.8);">{subtitulo}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Métrica rápida do top 5
    total_metrica = usuarios_data[metrica_principal].sum()
    if metrica_principal in ['total_views', 'total_likes']:
        valor_formatado = formatar_numero(total_metrica)
    else:
        valor_formatado = f"{total_metrica:.1f}" if metrica_principal == 'score_performance' else f"{int(total_metrica)}"
    
    st.metric(f"{icone_metrica} Total Top 5", valor_formatado)
    
    # Lista dos top 5
    for i, (_, user) in enumerate(usuarios_data.head(5).iterrows(), 1):
        if metrica_principal == 'score_performance':
            categoria, cor = user['categoria_performance'], user['cor_categoria']
            valor_principal = f"Score: {user[metrica_principal]:.1f}/100"
            valor_secundario = categoria
        elif metrica_principal == 'total_views':
            cor = "#007bff"
            valor_principal = f"👁️ {formatar_numero(user[metrica_principal])} views"
            valor_secundario = f"🎥 {user[metrica_secundaria]} vídeos"
        elif metrica_principal == 'total_videos':
            cor = "#28a745"
            valor_principal = f"🎥 {user[metrica_principal]} vídeos"
            valor_secundario = f"📊 {formatar_numero(user[metrica_secundaria])} views/vídeo"
        elif metrica_principal == 'total_likes':
            cor = "#dc3545"
            valor_principal = f"❤️ {formatar_numero(user[metrica_principal])} curtidas"
            valor_secundario = f"📈 {user[metrica_secundaria]:.1f}% engajamento"
        
        # Truncar nome para não quebrar layout
        nome_truncado = user['discord_username'][:15] + "..." if len(user['discord_username']) > 15 else user['discord_username']
        
        st.markdown(f"""
        <div class="ranking-item" style="border-left: 4px solid {cor};">
            <strong>#{i} {nome_truncado}</strong><br>
            <small>{valor_principal}</small><br>
            <small>{valor_secundario}</small>
        </div>
        """, unsafe_allow_html=True)

def gerar_insights_usuario(usuario_data, df_usuarios):
    """Gera insights personalizados para um usuário"""
    insights = []
    recomendacoes = []
    
    # Verificar se é usuário inativo
    if usuario_data['total_views'] == 0:
        insights.append("😴 Usuário inativo - Nenhuma visualização registrada")
        recomendacoes.append("🚀 Comece publicando conteúdo nas plataformas disponíveis")
        recomendacoes.append("📅 Estabeleça uma rotina de postagem consistente")
        return insights, recomendacoes
    
    # Análise de posição (só para usuários ativos)
    usuarios_ativos = df_usuarios[df_usuarios['total_views'] > 0]
    total_usuarios_ativos = len(usuarios_ativos)
    rank_views = usuario_data['rank_views']
    rank_performance = usuario_data['rank_performance']
    
    # Insights de posição
    if rank_views <= total_usuarios_ativos * 0.1:
        insights.append("🏆 Você está no TOP 10% em visualizações!")
    elif rank_views <= total_usuarios_ativos * 0.25:
        insights.append("🥇 Você está no TOP 25% em visualizações!")
    
    if rank_performance <= total_usuarios_ativos * 0.1:
        insights.append("⭐ Performance excepcional - TOP 10% geral!")
    
    # Análise de engajamento
    taxa = usuario_data['taxa_engajamento']
    media_taxa = usuarios_ativos['taxa_engajamento'].mean()
    
    if taxa > media_taxa * 2:
        insights.append("🚀 Sua taxa de engajamento é DUPLA da média!")
        recomendacoes.append("📈 Aumente a frequência de posts para maximizar o alcance")
    elif taxa > media_taxa:
        insights.append("✅ Taxa de engajamento acima da média")
        recomendacoes.append("🎯 Analise seus melhores vídeos para replicar o sucesso")
    else:
        insights.append("📊 Há oportunidade para melhorar o engajamento")
        recomendacoes.append("💡 Use mais CTAs e interaja ativamente com comentários")
    
    # Análise de volume
    videos = usuario_data['total_videos']
    if videos > 100:
        insights.append("🎥 Criador muito ativo com grande volume de conteúdo")
        if taxa < media_taxa:
            recomendacoes.append("🎯 Foque na qualidade - menos posts, mais cuidado na produção")
    elif videos < 20:
        insights.append("🌱 Espaço para crescer com mais conteúdo")
        recomendacoes.append("📅 Estabeleça uma rotina de postagem consistente")
    
    # Análise de plataformas
    plataformas_ativas = []
    if usuario_data.get('tiktok_views', 0) > 0:
        plataformas_ativas.append('TikTok')
    if usuario_data.get('youtube_views', 0) > 0:
        plataformas_ativas.append('YouTube')
    if usuario_data.get('instagram_views', 0) > 0:
        plataformas_ativas.append('Instagram')
    
    if len(plataformas_ativas) == 1:
        recomendacoes.append(f"📱 Considere expandir além do {plataformas_ativas[0]} para diversificar")
    elif len(plataformas_ativas) >= 2:
        insights.append(f"🎯 Boa diversificação: ativo em {len(plataformas_ativas)} plataformas")
    
    return insights, recomendacoes

# ========== PÁGINAS AVANÇADAS ==========
def pagina_dashboard_executivo(df_usuarios):
    """Dashboard executivo com visão geral completa"""
    st.markdown('<div class="main-header"><h1>📊 Dashboard Executivo Completo</h1><p>Visão Geral de TODOS os Usuários</p></div>', unsafe_allow_html=True)
    
    if df_usuarios.empty:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    # Estatísticas gerais
    total_usuarios = len(df_usuarios)
    usuarios_ativos = len(df_usuarios[df_usuarios['total_views'] > 0])
    usuarios_inativos = total_usuarios - usuarios_ativos
    
    # KPIs principais
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">👥 Total</h3>
            <h2 style="margin: 0.5rem 0;">{total_usuarios}</h2>
            <p style="margin: 0; color: #666;">Usuários cadastrados</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">🟢 Ativos</h3>
            <h2 style="margin: 0.5rem 0;">{usuarios_ativos}</h2>
            <p style="margin: 0; color: #666;">{(usuarios_ativos/total_usuarios*100):.1f}% do total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #dc3545; margin: 0;">🔴 Inativos</h3>
            <h2 style="margin: 0.5rem 0;">{usuarios_inativos}</h2>
            <p style="margin: 0; color: #666;">{(usuarios_inativos/total_usuarios*100):.1f}% do total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_videos = df_usuarios['total_videos'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">🎥 Vídeos</h3>
            <h2 style="margin: 0.5rem 0;">{formatar_numero(total_videos)}</h2>
            <p style="margin: 0; color: #666;">Total publicados</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        total_views = df_usuarios['total_views'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">👁️ Views</h3>
            <h2 style="margin: 0.5rem 0;">{formatar_numero(total_views)}</h2>
            <p style="margin: 0; color: #666;">Total alcançadas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        usuarios_ativos_df = df_usuarios[df_usuarios['total_views'] > 0]
        engagement_medio = usuarios_ativos_df['taxa_engajamento'].mean() if not usuarios_ativos_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">📈 Engajamento</h3>
            <h2 style="margin: 0.5rem 0;">{engagement_medio:.1f}%</h2>
            <p style="margin: 0; color: #666;">Média usuários ativos</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Análise de distribuição
    col1, col2 = st.columns(2)
    
    with col1:
        # Status dos usuários
        status_counts = df_usuarios['status_usuario'].value_counts()
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="📊 Distribuição por Status de Atividade",
            color_discrete_sequence=['#28a745', '#ffc107', '#fd7e14', '#dc3545']
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Distribuição por categoria (só usuários ativos)
        usuarios_ativos_df = df_usuarios[df_usuarios['total_views'] > 0]
        if not usuarios_ativos_df.empty:
            dist_categoria = usuarios_ativos_df['categoria_performance'].value_counts()
            
            fig_cat = px.pie(
                values=dist_categoria.values,
                names=dist_categoria.index,
                title="🏆 Distribuição por Performance (Usuários Ativos)",
                color_discrete_sequence=['#ffd700', '#c0c0c0', '#cd7f32', '#4caf50', '#ff9800']
            )
            fig_cat.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("📊 Nenhum usuário ativo para análise de performance")
    
    st.divider()
    
    # Rankings detalhados em 4 categorias
    st.subheader("🏅 Rankings dos Campeões")
    
    # Verificar se há usuários ativos
    if usuarios_ativos_df.empty:
        st.info("📊 Nenhum usuário ativo encontrado para rankings")
    else:
        # Preparar dados dos rankings
        top_performance = usuarios_ativos_df.nlargest(5, 'score_performance')
        top_views = usuarios_ativos_df.nlargest(5, 'total_views')
        top_videos = usuarios_ativos_df.nlargest(5, 'total_videos')
        top_likes = usuarios_ativos_df.nlargest(5, 'total_likes')
        
        # Detectar se é mobile para ajustar layout
        is_mobile = st.session_state.get('is_mobile', False)
        
        # Layout responsivo: 4 colunas em desktop, 2x2 em tablet, 1 em mobile
        if st.sidebar.checkbox("📱 Forçar layout mobile", value=False, help="Teste o layout mobile"):
            # Layout mobile: 1 coluna
            criar_ranking_card(
                "🏆 Top Performance", 
                "Score baseado em métricas reais",
                "linear-gradient(135deg, #ffd700, #ffed4e)",
                top_performance, 'score_performance', 'categoria_performance', "📊"
            )
            
            criar_ranking_card(
                "👁️ Campeões de Views", 
                "Maior alcance total",
                "linear-gradient(135deg, #007bff, #66b3ff)",
                top_views, 'total_views', 'total_videos', "👁️"
            )
            
            criar_ranking_card(
                "🎥 Reis da Produção", 
                "Mais conteúdo criado",
                "linear-gradient(135deg, #28a745, #6fbf73)",
                top_videos, 'total_videos', 'media_views_por_video', "🎬"
            )
            
            criar_ranking_card(
                "❤️ Mais Amados", 
                "Maior engajamento total",
                "linear-gradient(135deg, #dc3545, #ff6b7a)",
                top_likes, 'total_likes', 'taxa_engajamento', "❤️"
            )
        else:
            # Layout desktop: 4 colunas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                criar_ranking_card(
                    "🏆 Top Performance", 
                    "Score baseado em métricas reais",
                    "linear-gradient(135deg, #ffd700, #ffed4e)",
                    top_performance, 'score_performance', 'categoria_performance', "📊"
                )
            
            with col2:
                criar_ranking_card(
                    "👁️ Campeões de Views", 
                    "Maior alcance total",
                    "linear-gradient(135deg, #007bff, #66b3ff)",
                    top_views, 'total_views', 'total_videos', "👁️"
                )
            
            with col3:
                criar_ranking_card(
                    "🎥 Reis da Produção", 
                    "Mais conteúdo criado",
                    "linear-gradient(135deg, #28a745, #6fbf73)",
                    top_videos, 'total_videos', 'media_views_por_video', "🎬"
                )
            
            with col4:
                criar_ranking_card(
                    "❤️ Mais Amados", 
                    "Maior engajamento total",
                    "linear-gradient(135deg, #dc3545, #ff6b7a)",
                    top_likes, 'total_likes', 'taxa_engajamento', "❤️"
                )
    
    # Estatísticas comparativas dos rankings
    if not usuarios_ativos_df.empty:
        st.divider()
        st.subheader("📈 Estatísticas dos Rankings")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score_medio = usuarios_ativos_df['score_performance'].mean()
            score_top1 = usuarios_ativos_df['score_performance'].max()
            delta_score = score_top1 - score_medio
            st.metric("🏆 Score Médio", f"{score_medio:.1f}", 
                     delta=f"+{delta_score:.1f} (vs top 1)",
                     help="Score médio vs melhor performance")
        
        with col2:
            views_media = usuarios_ativos_df['total_views'].mean()
            views_top1 = usuarios_ativos_df['total_views'].max()
            st.metric("👁️ Views Médias", formatar_numero(views_media),
                     delta=f"Top 1: {formatar_numero(views_top1)}",
                     help="Média vs campeão de views")
        
        with col3:
            videos_medio = usuarios_ativos_df['total_videos'].mean()
            videos_top1 = usuarios_ativos_df['total_videos'].max()
            st.metric("🎥 Vídeos Médios", f"{videos_medio:.1f}",
                     delta=f"Top 1: {videos_top1}",
                     help="Média vs maior produtor")
        
        with col4:
            likes_media = usuarios_ativos_df['total_likes'].mean()
            likes_top1 = usuarios_ativos_df['total_likes'].max()
            st.metric("❤️ Curtidas Médias", formatar_numero(likes_media),
                     delta=f"Top 1: {formatar_numero(likes_top1)}",
                     help="Média vs mais curtido")
        
        # Insights automáticos baseados nos dados
        st.markdown("#### 💡 Insights Automáticos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise de concentração
            top10_views = usuarios_ativos_df.nlargest(10, 'total_views')['total_views'].sum()
            total_views_all = usuarios_ativos_df['total_views'].sum()
            concentracao = (top10_views / total_views_all) * 100
            
            if concentracao > 80:
                nivel_concentracao = "🔴 Muito Alta"
                cor_insight = "#dc3545"
            elif concentracao > 60:
                nivel_concentracao = "🟡 Alta"
                cor_insight = "#ffc107"
            else:
                nivel_concentracao = "🟢 Equilibrada"
                cor_insight = "#28a745"
                
            st.markdown(f"""
            <div class="insight-box" style="border-left-color: {cor_insight};">
                <h5>📊 Concentração de Views</h5>
                <p>Top 10 detém <strong>{concentracao:.1f}%</strong> das views totais</p>
                <p>Nível: {nivel_concentracao}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Análise de engajamento
            engagement_medio = usuarios_ativos_df['taxa_engajamento'].mean()
            
            if engagement_medio > 5:
                qualidade_eng = "🟢 Excelente"
                cor_eng = "#28a745"
            elif engagement_medio > 3:
                qualidade_eng = "🟡 Boa"
                cor_eng = "#ffc107"
            else:
                qualidade_eng = "🔴 Precisa Melhorar"
                cor_eng = "#dc3545"
                
            st.markdown(f"""
            <div class="insight-box" style="border-left-color: {cor_eng};">
                <h5>📈 Qualidade do Engajamento</h5>
                <p>Taxa média: <strong>{engagement_medio:.2f}%</strong></p>
                <p>Qualidade: {qualidade_eng}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Seção de usuários inativos (expandível para não poluir)
    st.divider()
    usuarios_inativos_df = df_usuarios[df_usuarios['total_views'] == 0]
    
    if not usuarios_inativos_df.empty:
        with st.expander(f"😴 Usuários Inativos ({len(usuarios_inativos_df)})", expanded=False):
            st.warning(f"⚠️ {len(usuarios_inativos_df)} usuários sem visualizações")
            
            # Porcentagem de inativos
            porcentagem_inativos = (len(usuarios_inativos_df) / len(df_usuarios)) * 100
            st.metric("📊 Taxa de Inatividade", f"{porcentagem_inativos:.1f}%")
            
            # Mostrar em colunas para organizar melhor
            num_cols = 3
            cols = st.columns(num_cols)
            
            for i, (_, user) in enumerate(usuarios_inativos_df.head(15).iterrows()):
                col_idx = i % num_cols
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="zero-user-card">
                        <strong>{user['discord_username']}</strong><br>
                        <small>😴 Sem atividade registrada</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            if len(usuarios_inativos_df) > 15:
                st.info(f"➕ E mais {len(usuarios_inativos_df) - 15} usuários inativos...")
                
            # Ações sugeridas para usuários inativos
            st.markdown("""
            <div class="warning-box">
                <h4>💡 Ações Sugeridas para Reativação:</h4>
                <ul>
                    <li>🎯 Criar campanha de onboarding</li>
                    <li>📧 Enviar tutoriais passo a passo</li>
                    <li>🎁 Programa de incentivos para primeira postagem</li>
                    <li>👥 Mentoria com usuários ativos</li>
                    <li>📊 Analisar barreiras de entrada</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 Todos os usuários têm atividade!")

def pagina_rankings_completos(df_usuarios):
    """Rankings completos com controle de visualização"""
    st.markdown('<div class="main-header"><h1>🏆 Rankings Completos</h1><p>Controle Total sobre Visualizações</p></div>', unsafe_allow_html=True)
    
    if df_usuarios.empty:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    # Controles avançados
    st.subheader("🎛️ Controles de Visualização")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        incluir_inativos = st.checkbox("😴 Incluir usuários inativos", value=False, help="Mostrar usuários com 0 views")
    
    with col2:
        if incluir_inativos:
            max_usuarios = len(df_usuarios)
            opcoes_top = [10, 20, 30, 50, 100, max_usuarios]
            labels_top = [f"Top {x}" for x in opcoes_top[:-1]] + [f"Todos ({max_usuarios})"]
        else:
            usuarios_ativos = df_usuarios[df_usuarios['total_views'] > 0]
            max_usuarios = len(usuarios_ativos)
            opcoes_top = [10, 20, 30, 50, 100, max_usuarios]
            labels_top = [f"Top {x}" for x in opcoes_top[:-1]] + [f"Todos ativos ({max_usuarios})"]
        
        top_n_idx = st.selectbox("📊 Quantidade no ranking:", range(len(opcoes_top)), format_func=lambda x: labels_top[x], index=1)
        top_n = opcoes_top[top_n_idx]
    
    with col3:
        mostrar_graficos = st.checkbox("📈 Mostrar gráficos", value=True)
    
    with col4:
        formato_grafico = st.selectbox("📊 Tipo de gráfico:", ["Barras Horizontais", "Barras Verticais", "Apenas Tabela"])
    
    # Filtrar dados baseado na seleção
    if incluir_inativos:
        df_trabalho = df_usuarios.copy()
        st.info(f"📊 Mostrando dados de {len(df_trabalho)} usuários (incluindo {len(df_usuarios[df_usuarios['total_views'] == 0])} inativos)")
    else:
        df_trabalho = df_usuarios[df_usuarios['total_views'] > 0].copy()
        inativos_ocultos = len(df_usuarios) - len(df_trabalho)
        if inativos_ocultos > 0:
            st.info(f"📊 Mostrando apenas usuários ativos. {inativos_ocultos} usuários inativos ocultos.")
    
    if df_trabalho.empty:
        st.warning("⚠️ Nenhum usuário encontrado com os filtros aplicados")
        return
    
    st.divider()
    
    # Abas dos rankings
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👁️ Mais Views", "❤️ Mais Curtidas", "📈 Melhor Engajamento", 
        "🏆 Score Performance", "📱 Por Plataforma"
    ])
    
    with tab1:
        st.subheader(f"👁️ Ranking por Visualizações")
        top_views = df_trabalho.nlargest(top_n, 'total_views')
        
        if mostrar_graficos and formato_grafico != "Apenas Tabela":
            if formato_grafico == "Barras Horizontais":
                fig = px.bar(
                    top_views,
                    x='total_views',
                    y='discord_username',
                    orientation='h',
                    title=f"Ranking por Visualizações",
                    color='total_views',
                    color_continuous_scale='Blues',
                    text='total_views'
                )
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_yaxes(categoryorder='total ascending')
                fig.update_layout(height=max(400, min(len(top_views) * 25, 800)), showlegend=False)
            else:  # Barras Verticais
                fig = px.bar(
                    top_views.head(20),  # Limit to 20 for vertical bars
                    x='discord_username',
                    y='total_views',
                    title=f"Top 20 - Visualizações",
                    color='total_views',
                    color_continuous_scale='Blues'
                )
                fig.update_xaxes(tickangle=45)
                fig.update_layout(height=600, showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        df_display = top_views[['discord_username', 'total_views', 'total_videos', 'media_views_por_video', 'status_usuario']].copy()
        
        # Adicionar indicadores visuais para usuários inativos
        if incluir_inativos:
            df_display['indicador'] = df_display.apply(
                lambda x: "😴 INATIVO" if x['total_views'] == 0 else "🟢 ATIVO", axis=1
            )
            colunas_ordem = ['indicador', 'discord_username', 'total_views', 'total_videos', 'media_views_por_video', 'status_usuario']
        else:
            colunas_ordem = ['discord_username', 'total_views', 'total_videos', 'media_views_por_video', 'status_usuario']
        
        st.dataframe(
            df_display[colunas_ordem],
            column_config={
                "indicador": "🚦 Status",
                "discord_username": "👤 Usuário",
                "total_views": st.column_config.NumberColumn("👁️ Views Totais", format="%d"),
                "total_videos": "🎥 Vídeos",
                "media_views_por_video": st.column_config.NumberColumn("📊 Média/Vídeo", format="%.0f"),
                "status_usuario": "📊 Status"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Estatísticas adicionais
        st.markdown("#### 📈 Estatísticas do Ranking")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Mostrado", len(top_views))
        with col2:
            st.metric("👁️ Views Totais", formatar_numero(top_views['total_views'].sum()))
        with col3:
            st.metric("🎥 Vídeos Totais", formatar_numero(top_views['total_videos'].sum()))
        with col4:
            views_ativas = top_views[top_views['total_views'] > 0]['total_views']
            st.metric("📊 Média Views", formatar_numero(views_ativas.mean()) if not views_ativas.empty else "0")
    
    with tab2:
        st.subheader(f"❤️ Ranking por Curtidas")
        top_likes = df_trabalho.nlargest(top_n, 'total_likes')
        
        if mostrar_graficos and formato_grafico != "Apenas Tabela":
            if formato_grafico == "Barras Horizontais":
                fig = px.bar(
                    top_likes,
                    x='total_likes',
                    y='discord_username',
                    orientation='h',
                    title=f"Ranking por Curtidas",
                    color='total_likes',
                    color_continuous_scale='Reds'
                )
                fig.update_yaxes(categoryorder='total ascending')
                fig.update_layout(height=max(400, min(len(top_likes) * 25, 800)), showlegend=False)
            else:
                fig = px.bar(
                    top_likes.head(20),
                    x='discord_username',
                    y='total_likes',
                    title=f"Top 20 - Curtidas",
                    color='total_likes',
                    color_continuous_scale='Reds'
                )
                fig.update_xaxes(tickangle=45)
                fig.update_layout(height=600, showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
        
        df_display = top_likes[['discord_username', 'total_likes', 'total_views', 'media_likes_por_video', 'taxa_engajamento']].copy()
        st.dataframe(
            df_display,
            column_config={
                "discord_username": "👤 Usuário",
                "total_likes": st.column_config.NumberColumn("❤️ Curtidas", format="%d"),
                "total_views": st.column_config.NumberColumn("👁️ Views", format="%d"),
                "media_likes_por_video": st.column_config.NumberColumn("💖 Média/Vídeo", format="%.0f"),
                "taxa_engajamento": st.column_config.NumberColumn("📈 Engajamento %", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tab3:
        st.subheader(f"📈 Ranking por Engajamento")
        
        # Para engajamento, filtrar apenas usuários com dados significativos
        df_engajamento = df_trabalho[df_trabalho['total_views'] >= 100] if not incluir_inativos else df_trabalho[df_trabalho['total_views'] > 0]
        
        if df_engajamento.empty:
            st.warning("⚠️ Nenhum usuário com dados suficientes para análise de engajamento")
        else:
            top_engagement = df_engajamento.nlargest(min(top_n, len(df_engajamento)), 'taxa_engajamento')
            
            if mostrar_graficos and formato_grafico != "Apenas Tabela":
                if formato_grafico == "Barras Horizontais":
                    fig = px.bar(
                        top_engagement,
                        x='taxa_engajamento',
                        y='discord_username',
                        orientation='h',
                        title=f"Ranking por Taxa de Engajamento",
                        color='taxa_engajamento',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_yaxes(categoryorder='total ascending')
                    fig.update_layout(height=max(400, min(len(top_engagement) * 25, 800)), showlegend=False)
                else:
                    fig = px.bar(
                        top_engagement.head(20),
                        x='discord_username',
                        y='taxa_engajamento',
                        title=f"Top 20 - Engajamento",
                        color='taxa_engajamento',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_xaxes(tickangle=45)
                    fig.update_layout(height=600, showlegend=False)
                
                st.plotly_chart(fig, use_container_width=True)
            
            df_display = top_engagement[['discord_username', 'taxa_engajamento', 'total_views', 'total_interactions', 'consistencia']].copy()
            st.dataframe(
                df_display,
                column_config={
                    "discord_username": "👤 Usuário",
                    "taxa_engajamento": st.column_config.NumberColumn("📈 Taxa %", format="%.2f"),
                    "total_views": st.column_config.NumberColumn("👁️ Views", format="%d"),
                    "total_interactions": st.column_config.NumberColumn("💬 Interações", format="%d"),
                    "consistencia": "🎯 Consistência"
                },
                hide_index=True,
                use_container_width=True
            )
    
    with tab4:
        st.subheader(f"🏆 Ranking por Score de Performance")
        top_score = df_trabalho.nlargest(top_n, 'score_performance')
        
        if mostrar_graficos and formato_grafico != "Apenas Tabela":
            if formato_grafico == "Barras Horizontais":
                fig = px.bar(
                    top_score,
                    x='score_performance',
                    y='discord_username',
                    orientation='h',
                    title=f"Ranking por Score de Performance",
                    color='score_performance',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_yaxes(categoryorder='total ascending')
                fig.update_layout(height=max(400, min(len(top_score) * 25, 800)), showlegend=False)
            else:
                fig = px.bar(
                    top_score.head(20),
                    x='discord_username',
                    y='score_performance',
                    title=f"Top 20 - Performance",
                    color='score_performance',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_xaxes(tickangle=45)
                fig.update_layout(height=600, showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
        
        df_display = top_score[['discord_username', 'score_performance', 'categoria_performance', 'plataforma_principal', 'taxa_engajamento']].copy()
        
        # Formatar plataforma principal
        df_display['plataforma_principal'] = df_display['plataforma_principal'].fillna('Geral').str.title()
        
        st.dataframe(
            df_display,
            column_config={
                "discord_username": "👤 Usuário",
                "score_performance": st.column_config.NumberColumn("🏆 Score", format="%.1f"),
                "categoria_performance": "📊 Categoria", 
                "plataforma_principal": "📱 Plataforma Principal",
                "taxa_engajamento": st.column_config.NumberColumn("📈 Engajamento %", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tab5:
        st.subheader("📱 Rankings por Plataforma")
        
        plat_tabs = st.tabs(["🎵 TikTok", "📺 YouTube", "📸 Instagram"])
        
        with plat_tabs[0]:  # TikTok
            tiktok_users = df_trabalho[df_trabalho['tiktok_views'] > 0]
            if not tiktok_users.empty:
                top_tiktok = tiktok_users.nlargest(min(top_n, len(tiktok_users)), 'tiktok_views')
                
                if mostrar_graficos and formato_grafico != "Apenas Tabela":
                    fig = px.bar(
                        top_tiktok,
                        x='tiktok_views',
                        y='discord_username',
                        orientation='h',
                        title="Ranking TikTok - Views",
                        color='tiktok_views',
                        color_continuous_scale='Blues'
                    )
                    fig.update_yaxes(categoryorder='total ascending')
                    fig.update_layout(height=max(400, min(len(top_tiktok) * 25, 600)), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(
                    top_tiktok[['discord_username', 'tiktok_views', 'tiktok_videos']],
                    column_config={
                        "discord_username": "👤 Usuário",
                        "tiktok_views": st.column_config.NumberColumn("🎵 TikTok Views", format="%d"),
                        "tiktok_videos": "🎥 Vídeos"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("📊 Nenhum dado do TikTok encontrado")
        
        with plat_tabs[1]:  # YouTube
            youtube_users = df_trabalho[df_trabalho['youtube_views'] > 0]
            if not youtube_users.empty:
                top_youtube = youtube_users.nlargest(min(top_n, len(youtube_users)), 'youtube_views')
                
                if mostrar_graficos and formato_grafico != "Apenas Tabela":
                    fig = px.bar(
                        top_youtube,
                        x='youtube_views',
                        y='discord_username',
                        orientation='h',
                        title="Ranking YouTube - Views",
                        color='youtube_views',
                        color_continuous_scale='Reds'
                    )
                    fig.update_yaxes(categoryorder='total ascending')
                    fig.update_layout(height=max(400, min(len(top_youtube) * 25, 600)), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(
                    top_youtube[['discord_username', 'youtube_views', 'youtube_videos']],
                    column_config={
                        "discord_username": "👤 Usuário",
                        "youtube_views": st.column_config.NumberColumn("📺 YouTube Views", format="%d"),
                        "youtube_videos": "🎥 Vídeos"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("📊 Nenhum dado do YouTube encontrado")
        
        with plat_tabs[2]:  # Instagram
            instagram_users = df_trabalho[df_trabalho['instagram_views'] > 0]
            if not instagram_users.empty:
                top_instagram = instagram_users.nlargest(min(top_n, len(instagram_users)), 'instagram_views')
                
                if mostrar_graficos and formato_grafico != "Apenas Tabela":
                    fig = px.bar(
                        top_instagram,
                        x='instagram_views',
                        y='discord_username',
                        orientation='h',
                        title="Ranking Instagram - Views",
                        color='instagram_views',
                        color_continuous_scale='Purples'
                    )
                    fig.update_yaxes(categoryorder='total ascending')
                    fig.update_layout(height=max(400, min(len(top_instagram) * 25, 600)), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(
                    top_instagram[['discord_username', 'instagram_views', 'instagram_videos']],
                    column_config={
                        "discord_username": "👤 Usuário",
                        "instagram_views": st.column_config.NumberColumn("📸 Instagram Views", format="%d"),
                        "instagram_videos": "🎥 Vídeos"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("📊 Nenhum dado do Instagram encontrado")

def pagina_analise_usuario_avancada(df_usuarios):
    """Análise avançada individual do usuário"""
    st.markdown('<div class="main-header"><h1>👤 Análise Individual Completa</h1><p>Insights Detalhados para Qualquer Usuário</p></div>', unsafe_allow_html=True)
    
    if df_usuarios.empty:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    # Seleção do usuário com busca
    st.subheader("🔍 Seleção de Usuário")
    usuarios = sorted(df_usuarios['discord_username'].tolist())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        usuario_selecionado = st.selectbox("👤 Escolha o usuário para análise:", usuarios)
    
    with col2:
        # Mostrar estatísticas de seleção
        total_usuarios = len(usuarios)
        usuarios_ativos = len(df_usuarios[df_usuarios['total_views'] > 0])
        st.metric("📊 Total de Usuários", f"{total_usuarios}")
        st.metric("🟢 Usuários Ativos", f"{usuarios_ativos}")
    
    if usuario_selecionado:
        dados_usuario = df_usuarios[df_usuarios['discord_username'] == usuario_selecionado].iloc[0]
        
        # Verificar se é usuário ativo ou inativo
        eh_inativo = dados_usuario['total_views'] == 0
        
        # Header do usuário
        if eh_inativo:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #6c757d22, #6c757d11); 
                        border: 2px solid #6c757d; color: #333; padding: 2rem; 
                        border-radius: 15px; margin: 1rem 0; text-align: center;">
                <h2>😴 {usuario_selecionado}</h2>
                <h3 style="color: #6c757d;">USUÁRIO INATIVO</h3>
                <p><strong>Status:</strong> Nenhuma atividade registrada</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            categoria, cor = dados_usuario['categoria_performance'], dados_usuario['cor_categoria']
            plataforma_principal = dados_usuario.get('plataforma_principal', 'Geral')
            plataforma_emoji = {'tiktok': '🎵', 'youtube': '📺', 'instagram': '📸'}.get(plataforma_principal, '📱')
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {cor}22, {cor}11); 
                        border: 2px solid {cor}; color: #333; padding: 2rem; 
                        border-radius: 15px; margin: 1rem 0; text-align: center;">
                <h2>🎯 {usuario_selecionado}</h2>
                <h3 style="color: {cor};">{categoria}</h3>
                <p><strong>Score de Performance:</strong> {dados_usuario['score_performance']:.1f}/100</p>
                <p><strong>Plataforma Principal:</strong> {plataforma_emoji} {plataforma_principal.title()}</p>
                <small>Taxa calculada usando fórmula oficial do {plataforma_principal.title()}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Métricas principais
        if eh_inativo:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="stats-box">
                    <h4>😴 Status</h4>
                    <p>Usuário Inativo</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="stats-box">
                    <h4>📊 Dados</h4>
                    <p>Nenhum registro</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div class="stats-box">
                    <h4>🚀 Potencial</h4>
                    <p>Aguardando ativação</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "🏆 Posição Geral",
                    f"#{dados_usuario['rank_performance']}" if dados_usuario['rank_performance'] > 0 else "N/A",
                    help="Posição no ranking geral de performance"
                )
            
            with col2:
                st.metric(
                    "🎥 Vídeos",
                    int(dados_usuario['total_videos']),
                    help="Total de vídeos publicados"
                )
            
            with col3:
                st.metric(
                    "👁️ Views Totais",
                    formatar_numero(dados_usuario['total_views']),
                    help="Total de visualizações"
                )
            
            with col4:
                st.metric(
                    "❤️ Curtidas",
                    formatar_numero(dados_usuario['total_likes']),
                    help="Total de curtidas recebidas"
                )
            
            with col5:
                st.metric(
                    "📈 Engajamento",
                    f"{dados_usuario['taxa_engajamento']:.1f}%",
                    help="Taxa de engajamento média"
                )
        
        st.divider()
        
        if eh_inativo:
            # Análise para usuário inativo
            st.subheader("😴 Análise de Usuário Inativo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="warning-box">
                    <h4>⚠️ Status Atual</h4>
                    <p>Este usuário não possui nenhuma atividade registrada no sistema.</p>
                    <ul>
                        <li>0 vídeos publicados</li>
                        <li>0 visualizações</li>
                        <li>0 interações</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="success-box">
                    <h4>🚀 Próximos Passos Recomendados</h4>
                    <ul>
                        <li>📱 Configurar contas nas plataformas</li>
                        <li>🎥 Publicar primeiro vídeo</li>
                        <li>📅 Estabelecer rotina de postagem</li>
                        <li>🎯 Definir nicho de conteúdo</li>
                        <li>💡 Estudar tendências da área</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Estatísticas gerais para contexto
            st.subheader("📊 Contexto Geral da Plataforma")
            usuarios_ativos = df_usuarios[df_usuarios['total_views'] > 0]
            
            if not usuarios_ativos.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Média de Views", formatar_numero(usuarios_ativos['total_views'].mean()))
                with col2:
                    st.metric("🎥 Média de Vídeos", f"{usuarios_ativos['total_videos'].mean():.0f}")
                with col3:
                    st.metric("📈 Engajamento Médio", f"{usuarios_ativos['taxa_engajamento'].mean():.1f}%")
                with col4:
                    st.metric("🏆 Score Médio", f"{usuarios_ativos['score_performance'].mean():.1f}")
                
                st.info("💡 **Dica:** Estes são os números médios dos usuários ativos. Use como referência para suas primeiras metas!")
        
        else:
            # Análise detalhada para usuário ativo
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Comparação com a média
                st.subheader("📊 Comparação com Usuários Ativos")
                
                usuarios_ativos = df_usuarios[df_usuarios['total_views'] > 0]
                media_views = usuarios_ativos['total_views'].mean()
                media_likes = usuarios_ativos['total_likes'].mean()
                media_engagement = usuarios_ativos['taxa_engajamento'].mean()
                media_videos = usuarios_ativos['total_videos'].mean()
                
                comparacao_data = {
                    'Métrica': ['Views', 'Curtidas', 'Engajamento %', 'Vídeos'],
                    'Usuário': [
                        dados_usuario['total_views'],
                        dados_usuario['total_likes'],
                        dados_usuario['taxa_engajamento'],
                        dados_usuario['total_videos']
                    ],
                    'Média Geral': [media_views, media_likes, media_engagement, media_videos]
                }
                
                df_comp = pd.DataFrame(comparacao_data)
                
                fig_comp = px.bar(
                    df_comp,
                    x='Métrica',
                    y=['Usuário', 'Média Geral'],
                    title="Comparação: Usuário vs Média de Usuários Ativos",
                    barmode='group',
                    color_discrete_sequence=['#667eea', '#764ba2']
                )
                st.plotly_chart(fig_comp, use_container_width=True)
                
                # Análise de plataformas
                st.subheader("📱 Distribuição por Plataforma")
                
                plataformas = {
                    'TikTok': dados_usuario.get('tiktok_views', 0),
                    'YouTube': dados_usuario.get('youtube_views', 0),
                    'Instagram': dados_usuario.get('instagram_views', 0)
                }
                
                plataformas_ativas = {k: v for k, v in plataformas.items() if v > 0}
                
                if plataformas_ativas:
                    fig_pie = px.pie(
                        values=list(plataformas_ativas.values()),
                        names=list(plataformas_ativas.keys()),
                        title="Distribuição de Views por Plataforma",
                        color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Detalhes por plataforma
                    st.markdown("#### 📋 Detalhes por Plataforma")
                    for plat, views in plataformas_ativas.items():
                        porcentagem = (views / dados_usuario['total_views']) * 100
                        videos = dados_usuario.get(f'{plat.lower()}_videos', 0)
                        media_plat = (views / videos) if videos > 0 else 0
                        
                        st.markdown(f"""
                        <div class="ranking-card">
                            <h4>{plat}</h4>
                            <p><strong>Views:</strong> {formatar_numero(views)} ({porcentagem:.1f}% do total)</p>
                            <p><strong>Vídeos:</strong> {videos}</p>
                            <p><strong>Média/Vídeo:</strong> {formatar_numero(media_plat)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("📱 Dados detalhados por plataforma não disponíveis")
            
            with col2:
                # Rankings específicos
                st.subheader("🏆 Posições nos Rankings")
                
                rankings = [
                    ("👁️ Views", dados_usuario['rank_views'], len(usuarios_ativos)),
                    ("❤️ Curtidas", dados_usuario['rank_likes'], len(usuarios_ativos)),
                    ("📈 Engajamento", dados_usuario['rank_engajamento'], len(usuarios_ativos)),
                    ("🏆 Performance", dados_usuario['rank_performance'], len(usuarios_ativos))
                ]
                
                for nome, posicao, total in rankings:
                    if posicao > 0:  # Só mostrar se tem ranking
                        percentil = (1 - posicao / total) * 100
                        if percentil >= 90:
                            cor = "#ffd700"
                            nivel = "TOP 10%"
                        elif percentil >= 75:
                            cor = "#c0c0c0"
                            nivel = "TOP 25%"
                        elif percentil >= 50:
                            cor = "#cd7f32"
                            nivel = "TOP 50%"
                        else:
                            cor = "#666"
                            nivel = f"TOP {percentil:.0f}%"
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; 
                                    border-left: 4px solid {cor}; margin: 0.5rem 0;">
                            <strong>{nome}</strong><br>
                            <span style="font-size: 1.2em;">#{int(posicao)}</span> de {total}<br>
                            <small style="color: {cor}; font-weight: bold;">{nivel}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Insights e recomendações
                st.subheader("💡 Insights Personalizados")
                
                insights, recomendacoes = gerar_insights_usuario(dados_usuario, df_usuarios)
                
                if insights:
                    for insight in insights:
                        st.markdown(f"""
                        <div class="insight-box">
                            <p style="margin: 0;"><strong>{insight}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if recomendacoes:
                    st.subheader("🎯 Recomendações")
                    for rec in recomendacoes:
                        st.markdown(f"""
                        <div class="warning-box">
                            <p style="margin: 0;">{rec}</p>
                        </div>
                        """, unsafe_allow_html=True)

def pagina_videos_completa(df_videos):
    """Análise completa de TODOS os vídeos"""
    st.markdown('<div class="main-header"><h1>🎬 Análise Completa de Vídeos</h1><p>Todos os Vídeos com Links e Filtros Avançados</p></div>', unsafe_allow_html=True)
    
    # Mostrar estatísticas do carregamento
    if 'total_videos_banco' in st.session_state and 'videos_carregados' in st.session_state:
        total_banco = st.session_state['total_videos_banco']
        carregados = st.session_state['videos_carregados']
        
        if carregados < total_banco:
            st.warning(f"⚠️ Carregados {carregados:,} de {total_banco:,} vídeos do banco. Alguns vídeos podem não ter usuário associado.")
        else:
            st.success(f"✅ Todos os {carregados:,} vídeos carregados com sucesso!")
    
    if df_videos.empty:
        st.error("⚠️ Nenhum vídeo encontrado no banco de dados")
        return
    
    # Estatísticas gerais
    total_videos = len(df_videos)
    videos_com_link = len(df_videos[df_videos['tem_link'] == True]) if 'tem_link' in df_videos.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎬 Total de Vídeos", f"{total_videos:,}")
    with col2:
        st.metric("🔗 Com Links", f"{videos_com_link:,}")
    with col3:
        porcentagem_links = (videos_com_link / total_videos * 100) if total_videos > 0 else 0
        st.metric("📊 % com Links", f"{porcentagem_links:.1f}%")
    with col4:
        if 'views' in df_videos.columns:
            total_views_safe = pd.to_numeric(df_videos['views'], errors='coerce').fillna(0).sum()
            st.metric("👁️ Views Totais", formatar_numero(total_views_safe))
    
    st.divider()
    
    # Filtros avançados
    st.subheader("🎯 Filtros Avançados")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        plataformas = ['Todas'] + sorted(df_videos['platform'].dropna().unique().tolist()) if 'platform' in df_videos.columns else ['Todas']
        plataforma = st.selectbox("📱 Plataforma:", plataformas)
    
    with col2:
        usuarios = ['Todos'] + sorted(df_videos['discord_username'].dropna().unique().tolist()) if 'discord_username' in df_videos.columns else ['Todos']
        usuario = st.selectbox("👤 Usuário:", usuarios)
    
    with col3:
        min_views = st.number_input("👁️ Views mínimas:", min_value=0, value=0, step=100)
    
    with col4:
        apenas_com_link = st.checkbox("🔗 Apenas com links", value=False)
    
    with col5:
        ordenacao_opcoes = {
            "📅 Mais Recentes": ("id", False),
            "👁️ Mais Views": ("views", False),
            "❤️ Mais Curtidas": ("likes", False),
            "📈 Maior Engajamento": ("engagement_rate", False),
            "🏆 Melhor Score": ("video_score", False)
        }
        ordenacao = st.selectbox("🔄 Ordenar por:", list(ordenacao_opcoes.keys()))
    
    # Aplicar filtros
    df_filtrado = df_videos.copy()
    
    if plataforma != 'Todas' and 'platform' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['platform'] == plataforma]
    
    if usuario != 'Todos' and 'discord_username' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['discord_username'] == usuario]
    
    if 'views' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['views'] >= min_views]
    
    if apenas_com_link and 'tem_link' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['tem_link'] == True]
    
    # Aplicar ordenação
    coluna_ord, ascending = ordenacao_opcoes[ordenacao]
    if coluna_ord in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values(coluna_ord, ascending=ascending)
    
    # Mostrar resultados dos filtros
    st.info(f"🔍 Filtros aplicados: {len(df_filtrado):,} vídeos de {total_videos:,} total")
    
    st.divider()
    
    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Lista Paginada", "🏆 Top Vídeos", "📊 Análises", "🔍 Busca Avançada"
    ])
    
    with tab1:
        st.subheader("📋 Lista Completa de Vídeos")
        
        if df_filtrado.empty:
            st.warning("⚠️ Nenhum vídeo encontrado com os filtros aplicados")
        else:
            # Controles de paginação melhorados
            col1, col2, col3 = st.columns(3)
            
            with col1:
                videos_por_pagina = st.selectbox("Vídeos por página:", [10, 20, 50, 100], index=2)
            
            with col2:
                total_paginas = max(1, (len(df_filtrado) - 1) // videos_por_pagina + 1)
                pagina_atual = st.number_input("Página:", min_value=1, max_value=total_paginas, value=1)
            
            with col3:
                st.metric("📄 Total de Páginas", total_paginas)
            
            # Calcular range da página
            inicio = (pagina_atual - 1) * videos_por_pagina
            fim = min(inicio + videos_por_pagina, len(df_filtrado))
            df_pagina = df_filtrado.iloc[inicio:fim]
            
            st.info(f"📊 Mostrando vídeos {inicio + 1:,} a {fim:,} de {len(df_filtrado):,} filtrados")
            
            # Exibir vídeos
            for idx, (_, video) in enumerate(df_pagina.iterrows()):
                titulo = video.get('title', f'Vídeo #{video.get("id", idx+1)}')
                categoria = video.get('categoria_video', '📊 Sem categoria')
                
                with st.expander(f"{categoria} {titulo[:100]}..."):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        # Informações principais
                        st.markdown("#### 📋 Informações do Vídeo")
                        if 'discord_username' in video.index:
                            st.write(f"👤 **Criador:** {video['discord_username']}")
                        if 'platform' in video.index:
                            st.write(f"📱 **Plataforma:** {video['platform']}")
                        if 'title' in video.index:
                            st.write(f"📝 **Título:** {video['title']}")
                        
                        # Link do vídeo - DESTAQUE
                        if 'url' in video.index and pd.notna(video['url']) and video['url'] != '':
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #28a745, #20c997); 
                                        padding: 1.5rem; border-radius: 12px; margin: 1rem 0; text-align: center;">
                                <a href="{video['url']}" target="_blank" 
                                   style="color: white; text-decoration: none; font-weight: bold; font-size: 1.2em;">
                                    🔗 ASSISTIR VÍDEO ORIGINAL
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; 
                                        border: 2px dashed #dee2e6; margin: 1rem 0; text-align: center;">
                                <span style="color: #6c757d; font-weight: bold;">🔗 Link não disponível</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        # Métricas básicas
                        st.markdown("#### 📊 Métricas")
                        if 'views' in video.index:
                            st.metric("👁️ Views", formatar_numero(video['views']))
                        if 'likes' in video.index:
                            st.metric("❤️ Curtidas", formatar_numero(video['likes']))
                        if 'comments' in video.index:
                            st.metric("💬 Comentários", formatar_numero(video['comments']))
                    
                    with col3:
                        # Métricas avançadas
                        st.markdown("#### 🎯 Performance")
                        if 'engagement_rate' in video.index:
                            st.metric("📈 Engajamento", f"{video['engagement_rate']:.2f}%")
                        if 'video_score' in video.index:
                            st.metric("🏆 Score", f"{video['video_score']:.1f}")
                        if 'interactions' in video.index:
                            st.metric("💪 Interações", formatar_numero(video['interactions']))
            
            # Navegação da página
            if total_paginas > 1:
                st.divider()
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if pagina_atual > 1:
                        if st.button("⬅️ Página Anterior"):
                            st.rerun()
                
                with col2:
                    st.markdown(f"<div style='text-align: center;'><strong>Página {pagina_atual} de {total_paginas}</strong></div>", unsafe_allow_html=True)
                
                with col3:
                    if pagina_atual < total_paginas:
                        if st.button("Próxima Página ➡️"):
                            st.rerun()
    
    with tab2:
        st.subheader("🏆 Top Vídeos por Categoria")
        
        # Controle de quantidade
        top_quantidade = st.selectbox("📊 Quantidade no top:", [10, 20, 50, 100], index=1)
        
        subtabs = st.tabs(["👁️ Mais Views", "❤️ Mais Curtidas", "📈 Maior Engajamento", "🔗 Melhores com Links"])
        
        with subtabs[0]:  # Mais Views
            if 'views' in df_filtrado.columns and not df_filtrado.empty:
                top_views = df_filtrado.nlargest(top_quantidade, 'views')
                
                # Gráfico
                fig = px.bar(
                    top_views.head(20),  # Limitar gráfico a 20 para visualização
                    x='views',
                    y='title' if 'title' in top_views.columns else 'id',
                    orientation='h',
                    title=f"Top 20 Vídeos - Mais Views",
                    color='views',
                    color_continuous_scale='Blues'
                )
                fig.update_yaxes(categoryorder='total ascending')
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                # Lista detalhada
                for i, (_, video) in enumerate(top_views.iterrows(), 1):
                    st.markdown(f"""
                    <div class="video-card">
                        <h4>#{i} - {video.get('title', 'Sem título')[:80]}...</h4>
                        <p><strong>👤 Criador:</strong> {video.get('discord_username', 'N/A')}</p>
                        <p><strong>📱 Plataforma:</strong> {video.get('platform', 'N/A')}</p>
                        <p><strong>👁️ Views:</strong> {formatar_numero(video['views'])}</p>
                        <p><strong>❤️ Curtidas:</strong> {formatar_numero(video.get('likes', 0))}</p>
                        {'<p><strong>📈 Engajamento:</strong> ' + f"{video['engagement_rate']:.2f}%" + '</p>' if 'engagement_rate' in video.index else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'url' in video.index and pd.notna(video['url']) and video['url'] != '':
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #007bff, #0056b3); 
                                    padding: 1rem; border-radius: 8px; margin: 0.5rem 0; text-align: center;">
                            <a href="{video['url']}" target="_blank" 
                               style="color: white; text-decoration: none; font-weight: bold;">
                                🔗 ASSISTIR VÍDEO
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.divider()
            else:
                st.info("ℹ️ Dados de views não disponíveis")
        
        with subtabs[1]:  # Mais Curtidas
            if 'likes' in df_filtrado.columns and not df_filtrado.empty:
                top_likes = df_filtrado.nlargest(top_quantidade, 'likes')
                
                for i, (_, video) in enumerate(top_likes.iterrows(), 1):
                    st.markdown(f"""
                    <div class="video-card">
                        <h4>#{i} - {video.get('title', 'Sem título')[:80]}...</h4>
                        <p><strong>👤 Criador:</strong> {video.get('discord_username', 'N/A')}</p>
                        <p><strong>❤️ Curtidas:</strong> {formatar_numero(video['likes'])}</p>
                        <p><strong>👁️ Views:</strong> {formatar_numero(video.get('views', 0))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'url' in video.index and pd.notna(video['url']) and video['url'] != '':
                        st.markdown(f"🔗 **[Ver Vídeo Original]({video['url']})**")
                    
                    st.divider()
        
        with subtabs[2]:  # Maior Engajamento
            if 'engagement_rate' in df_filtrado.columns and not df_filtrado.empty:
                # Filtrar vídeos com pelo menos 100 views
                df_eng = df_filtrado[df_filtrado['views'] >= 100] if 'views' in df_filtrado.columns else df_filtrado
                top_engagement = df_eng.nlargest(top_quantidade, 'engagement_rate')
                
                for i, (_, video) in enumerate(top_engagement.iterrows(), 1):
                    st.markdown(f"""
                    <div class="video-card">
                        <h4>#{i} - {video.get('title', 'Sem título')[:80]}...</h4>
                        <p><strong>👤 Criador:</strong> {video.get('discord_username', 'N/A')}</p>
                        <p><strong>📈 Engajamento:</strong> {video['engagement_rate']:.2f}%</p>
                        <p><strong>👁️ Views:</strong> {formatar_numero(video.get('views', 0))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'url' in video.index and pd.notna(video['url']) and video['url'] != '':
                        st.markdown(f"🔗 **[Ver Vídeo Original]({video['url']})**")
                    
                    st.divider()
        
        with subtabs[3]:  # Melhores com Links
            videos_com_link = df_filtrado[df_filtrado['tem_link'] == True] if 'tem_link' in df_filtrado.columns else df_filtrado[df_filtrado['url'].notna() & (df_filtrado['url'] != '')]
            
            if not videos_com_link.empty:
                # Ordenar por views para mostrar os melhores
                if 'views' in videos_com_link.columns:
                    videos_com_link = videos_com_link.sort_values('views', ascending=False)
                
                st.success(f"✅ Encontrados {len(videos_com_link):,} vídeos com links disponíveis")
                
                top_com_links = videos_com_link.head(top_quantidade)
                
                for i, (_, video) in enumerate(top_com_links.iterrows(), 1):
                    st.markdown(f"""
                    <div class="video-card">
                        <h4>#{i} - {video.get('title', 'Sem título')[:80]}...</h4>
                        <p><strong>👤 Criador:</strong> {video.get('discord_username', 'N/A')}</p>
                        <p><strong>📱 Plataforma:</strong> {video.get('platform', 'N/A')}</p>
                        <p><strong>👁️ Views:</strong> {formatar_numero(video.get('views', 0))}</p>
                        <p><strong>❤️ Curtidas:</strong> {formatar_numero(video.get('likes', 0))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #28a745, #20c997); 
                                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
                        <a href="{video['url']}" target="_blank" 
                           style="color: white; text-decoration: none; font-weight: bold; font-size: 1.1em;">
                            🔗 ASSISTIR VÍDEO AGORA
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
            else:
                st.warning("⚠️ Nenhum vídeo com link encontrado nos filtros aplicados")
    
    with tab3:
        st.subheader("📊 Análises e Estatísticas")
        
        if df_filtrado.empty:
            st.warning("⚠️ Nenhum dado para análise")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribuição por plataforma
                if 'platform' in df_filtrado.columns:
                    dist_plat = df_filtrado['platform'].value_counts()
                    
                    fig_plat = px.pie(
                        values=dist_plat.values,
                        names=dist_plat.index,
                        title="📱 Distribuição por Plataforma"
                    )
                    st.plotly_chart(fig_plat, use_container_width=True)
            
            with col2:
                # Distribuição de engajamento
                if 'categoria_video' in df_filtrado.columns:
                    dist_cat = df_filtrado['categoria_video'].value_counts()
                    
                    fig_cat = px.bar(
                        x=dist_cat.index,
                        y=dist_cat.values,
                        title="📈 Distribuição por Categoria de Engajamento",
                        color=dist_cat.values,
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)
            
            # Estatísticas detalhadas
            st.subheader("📋 Estatísticas Detalhadas")
            
            if 'views' in df_filtrado.columns:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total de Vídeos", f"{len(df_filtrado):,}")
                with col2:
                    st.metric("👁️ Views Totais", formatar_numero(df_filtrado['views'].sum()))
                with col3:
                    st.metric("📈 Engajamento Médio", f"{df_filtrado['engagement_rate'].mean():.2f}%" if 'engagement_rate' in df_filtrado.columns else "N/A")
                with col4:
                    st.metric("🔗 Taxa com Links", f"{(len(df_filtrado[df_filtrado['tem_link'] == True]) / len(df_filtrado) * 100):.1f}%" if 'tem_link' in df_filtrado.columns and len(df_filtrado) > 0 else "N/A")
                
                # Tabela de estatísticas
                estatisticas = {
                    'Métrica': ['Views', 'Curtidas', 'Comentários', 'Engajamento %'],
                    'Média': [
                        df_filtrado['views'].mean(),
                        df_filtrado['likes'].mean() if 'likes' in df_filtrado.columns else 0,
                        df_filtrado['comments'].mean() if 'comments' in df_filtrado.columns else 0,
                        df_filtrado['engagement_rate'].mean() if 'engagement_rate' in df_filtrado.columns else 0
                    ],
                    'Mediana': [
                        df_filtrado['views'].median(),
                        df_filtrado['likes'].median() if 'likes' in df_filtrado.columns else 0,
                        df_filtrado['comments'].median() if 'comments' in df_filtrado.columns else 0,
                        df_filtrado['engagement_rate'].median() if 'engagement_rate' in df_filtrado.columns else 0
                    ],
                    'Máximo': [
                        df_filtrado['views'].max(),
                        df_filtrado['likes'].max() if 'likes' in df_filtrado.columns else 0,
                        df_filtrado['comments'].max() if 'comments' in df_filtrado.columns else 0,
                        df_filtrado['engagement_rate'].max() if 'engagement_rate' in df_filtrado.columns else 0
                    ]
                }
                
                df_stats = pd.DataFrame(estatisticas)
                
                st.dataframe(
                    df_stats,
                    column_config={
                        "Métrica": "📊 Métrica",
                        "Média": st.column_config.NumberColumn("📈 Média", format="%.2f"),
                        "Mediana": st.column_config.NumberColumn("📊 Mediana", format="%.2f"),
                        "Máximo": st.column_config.NumberColumn("🔝 Máximo", format="%.0f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
    
    with tab4:
        st.subheader("🔍 Busca Avançada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'title' in df_filtrado.columns:
                termo_busca = st.text_input(
                    "🔎 Buscar no título:", 
                    placeholder="Ex: tutorial, review, gameplay, como fazer...",
                    help="Digite palavras-chave para buscar nos títulos dos vídeos"
                )
                
                if termo_busca:
                    videos_encontrados = df_filtrado[
                        df_filtrado['title'].str.contains(termo_busca, case=False, na=False)
                    ]
                    
                    if not videos_encontrados.empty:
                        st.success(f"✅ Encontrados {len(videos_encontrados):,} vídeos com '{termo_busca}'")
                        
                        # Ordenar por views
                        if 'views' in videos_encontrados.columns:
                            videos_encontrados = videos_encontrados.sort_values('views', ascending=False)
                        
                        # Limitar a 50 resultados para performance
                        videos_mostrar = videos_encontrados.head(50)
                        
                        if len(videos_encontrados) > 50:
                            st.info(f"📊 Mostrando os 50 melhores de {len(videos_encontrados)} encontrados")
                        
                        for i, (_, video) in enumerate(videos_mostrar.iterrows(), 1):
                            st.markdown(f"""
                            <div class="video-card">
                                <h4>#{i} - {video['title']}</h4>
                                <p><strong>👤 Criador:</strong> {video.get('discord_username', 'N/A')}</p>
                                <p><strong>📱 Plataforma:</strong> {video.get('platform', 'N/A')}</p>
                                <p><strong>👁️ Views:</strong> {formatar_numero(video.get('views', 0))}</p>
                                <p><strong>❤️ Curtidas:</strong> {formatar_numero(video.get('likes', 0))}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'url' in video.index and pd.notna(video['url']) and video['url'] != '':
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #6f42c1, #5a2d91); 
                                            padding: 1rem; border-radius: 8px; margin: 0.5rem 0; text-align: center;">
                                    <a href="{video['url']}" target="_blank" 
                                       style="color: white; text-decoration: none; font-weight: bold;">
                                        🔗 VER VÍDEO
                                    </a>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.divider()
                    else:
                        st.warning(f"⚠️ Nenhum vídeo encontrado com o termo '{termo_busca}'")
            else:
                st.info("ℹ️ Campo de título não disponível para busca")
        
        with col2:
            # Busca por criador
            if 'discord_username' in df_filtrado.columns:
                st.markdown("#### 👤 Busca por Criador")
                
                criadores_unicos = sorted(df_filtrado['discord_username'].dropna().unique())
                criador_busca = st.selectbox("Selecione um criador:", [''] + criadores_unicos)
                
                if criador_busca:
                    videos_criador = df_filtrado[df_filtrado['discord_username'] == criador_busca]
                    
                    if not videos_criador.empty:
                        st.success(f"✅ {len(videos_criador)} vídeos de {criador_busca}")
                        
                        # Estatísticas do criador
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("🎥 Total Vídeos", len(videos_criador))
                            if 'views' in videos_criador.columns:
                                st.metric("👁️ Views Totais", formatar_numero(videos_criador['views'].sum()))
                        with col2:
                            if 'likes' in videos_criador.columns:
                                st.metric("❤️ Curtidas Totais", formatar_numero(videos_criador['likes'].sum()))
                            if 'engagement_rate' in videos_criador.columns:
                                st.metric("📈 Engajamento Médio", f"{videos_criador['engagement_rate'].mean():.2f}%")
                        
                        # Mostrar alguns vídeos do criador
                        st.markdown("#### 🎬 Últimos Vídeos")
                        videos_recentes = videos_criador.head(10)
                        
                        for i, (_, video) in enumerate(videos_recentes.iterrows(), 1):
                            with st.expander(f"🎥 {video.get('title', f'Vídeo #{i}')}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if 'views' in video.index:
                                        st.write(f"👁️ **Views:** {formatar_numero(video['views'])}")
                                    if 'likes' in video.index:
                                        st.write(f"❤️ **Curtidas:** {formatar_numero(video['likes'])}")
                                    if 'platform' in video.index:
                                        st.write(f"📱 **Plataforma:** {video['platform']}")
                                
                                with col2:
                                    if 'engagement_rate' in video.index:
                                        st.write(f"📈 **Engajamento:** {video['engagement_rate']:.2f}%")
                                    if 'url' in video.index and pd.notna(video['url']) and video['url'] != '':
                                        st.markdown(f"🔗 **[Ver Vídeo]({video['url']})**")
                                    else:
                                        st.write("🔗 **Link:** Não disponível")

# ========== FUNÇÃO PRINCIPAL ==========
def main():
    """Função principal do dashboard completo"""
    
    # Verificar se está em produção e mostrar banner
    if IS_PRODUCTION:
        st.markdown("""
        <div class="production-banner">
            🚀 Dashboard rodando em ambiente de produção | 
            ⚡ Cache otimizado | 
            🎯 Métricas reais das redes sociais
        </div>
        """, unsafe_allow_html=True)
    
    # Inicializar session state
    if 'mostrar_explicacao' not in st.session_state:
        st.session_state['mostrar_explicacao'] = False
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📈 TrendX Analytics - Métricas Reais</h1>
        <p>Dashboard com Fórmulas Oficiais das Redes Sociais</p>
        <small style="opacity: 0.8;">✨ Fórmulas reais do TikTok, YouTube e Instagram • 🎬 Todos os vídeos • 🔗 Links diretos • 💡 Análises precisas</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar banco de dados
    if not os.path.exists(DB_PATH):
        st.error(f"⚠️ Banco de dados não encontrado: {DB_PATH}")
        
        if IS_PRODUCTION:
            st.error("🚨 **ERRO CRÍTICO DE DEPLOY:** Banco de dados ausente!")
            st.info("🔧 **Para corrigir este erro:**")
            st.info("1. ✅ Certifique-se que o arquivo `trendx_bot.db` está no repositório")
            st.info("2. ✅ Verifique se o arquivo não está no `.gitignore`") 
            st.info("3. ✅ O arquivo deve estar na raiz do projeto (mesmo diretório que dashboard.py)")
            st.info("4. ✅ Faça um novo deploy incluindo o banco de dados")
            st.info("5. ✅ Confirme que o arquivo foi enviado corretamente para o servidor")
            
            st.code(f"""
# Estrutura esperada do projeto:
projeto/
├── dashboard.py
├── trendx_bot.db  ← Este arquivo está faltando!
├── requirements.txt
└── README.md
            """)
        else:
            st.info("🔍 Certifique-se de que o arquivo do banco está na mesma pasta do script.")
            st.info(f"📁 Arquivo esperado: `{DB_PATH}`")
        
        st.stop()
    
    # Verificar se o banco está acessível
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        conn.close()
        
        if not tabelas:
            st.error("❌ Banco de dados está vazio ou corrompido!")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Erro ao acessar banco de dados: {str(e)}")
        if IS_PRODUCTION:
            st.error("🚨 **ERRO DE CONECTIVIDADE:** Não foi possível conectar ao banco!")
        st.stop()
    
    # Carregar dados com indicador de progresso
    try:
        with st.spinner("🔄 Carregando TODOS os dados do banco..."):
            progress_bar = st.progress(0)
            
            # Carregar usuários
            progress_bar.progress(25)
            df_usuarios = carregar_dados_usuarios_completo()
            
            # Carregar vídeos
            progress_bar.progress(75)
            df_videos = carregar_videos_completo()
            
            progress_bar.progress(100)
            
            if not df_usuarios.empty or not df_videos.empty:
                st.success("✅ Dados carregados com sucesso!")
            else:
                st.warning("⚠️ Dados carregados, mas podem estar vazios")
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados do banco: {str(e)}")
        st.info("💡 **Possíveis soluções:**")
        st.info("1. Verifique se o arquivo do banco não está corrompido")
        st.info("2. Confirme se as tabelas 'cached_stats' e 'valid_videos' existem")
        st.info("3. Verifique se as colunas têm os tipos de dados corretos")
        
        if IS_PRODUCTION:
            st.error("🚨 **ERRO DE PRODUÇÃO:** Falha ao carregar dados!")
            st.info("🔧 **Ações recomendadas:**")
            st.info("- Verificar logs do servidor")
            st.info("- Confirmar integridade do banco de dados")
            st.info("- Fazer rollback para versão anterior se necessário")
        
        st.stop()
    
    # Verificar se dados foram carregados
    if df_usuarios.empty and df_videos.empty:
        st.error("❌ Nenhum dado encontrado no banco!")
        st.info("💡 Verifique se as tabelas 'cached_stats' e 'valid_videos' existem e têm dados.")
        
        # Diagnóstico adicional
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas_existentes = [t[0] for t in cursor.fetchall()]
            
            st.info(f"📋 Tabelas encontradas no banco: {', '.join(tabelas_existentes)}")
            
            # Contar registros se as tabelas existem
            if 'cached_stats' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM cached_stats")
                count_users = cursor.fetchone()[0]
                st.info(f"👥 Registros na tabela cached_stats: {count_users}")
            
            if 'valid_videos' in tabelas_existentes:
                cursor.execute("SELECT COUNT(*) FROM valid_videos")
                count_videos = cursor.fetchone()[0]
                st.info(f"🎬 Registros na tabela valid_videos: {count_videos}")
            
            conn.close()
            
        except Exception as e:
            st.error(f"Erro ao diagnosticar banco: {str(e)}")
        
        st.stop()
    
    # Sidebar de navegação
    st.sidebar.markdown("## 🧭 Navegação Principal")
    
    paginas = [
        "📊 Dashboard Executivo",
        "🏆 Rankings Completos", 
        "👤 Análise Individual",
        "🎬 Vídeos Completos",
        "🔗 Gestão de Contas"
    ]
    
    # Adicionar ícones e descrições
    descricoes = [
        "Visão geral de todos os usuários",
        "Rankings com controles avançados",
        "Análise detalhada por usuário",
        "Todos os vídeos com links",
        "Identificar links e gerenciar contas"
    ]
    
    pagina_selecionada = st.sidebar.radio(
        "Escolha a análise:",
        paginas,
        help="Selecione a página de análise desejada"
    )
    
    # Mostrar descrição da página selecionada
    idx_pagina = paginas.index(pagina_selecionada)
    st.sidebar.info(f"📋 {descricoes[idx_pagina]}")
    
    # Status dos dados na sidebar
    st.sidebar.divider()
    st.sidebar.markdown("### 📊 Status Completo dos Dados")
    
    # Estatísticas dos usuários
    if not df_usuarios.empty:
        total_usuarios = len(df_usuarios)
        usuarios_ativos = len(df_usuarios[df_usuarios['total_views'] > 0])
        usuarios_inativos = total_usuarios - usuarios_ativos
        
        st.sidebar.metric("👥 Total Usuários", f"{total_usuarios:,}")
        st.sidebar.metric("🟢 Usuários Ativos", f"{usuarios_ativos:,}")
        st.sidebar.metric("😴 Usuários Inativos", f"{usuarios_inativos:,}")
        
        if usuarios_ativos > 0:
            taxa_ativacao = (usuarios_ativos / total_usuarios) * 100
            st.sidebar.metric("📈 Taxa de Ativação", f"{taxa_ativacao:.1f}%")
    
    # Estatísticas dos vídeos
    if not df_videos.empty:
        st.sidebar.divider()
        st.sidebar.markdown("### 🎬 Estatísticas de Vídeos")
        
        total_videos = len(df_videos)
        st.sidebar.metric("🎥 Total de Vídeos", f"{total_videos:,}")
        
        if 'tem_link' in df_videos.columns:
            videos_com_link = len(df_videos[df_videos['tem_link'] == True])
            st.sidebar.metric("🔗 Com Links", f"{videos_com_link:,}")
            
            if total_videos > 0:
                porcentagem_links = (videos_com_link / total_videos) * 100
                st.sidebar.metric("📊 % com Links", f"{porcentagem_links:.1f}%")
        
        if 'views' in df_videos.columns:
            total_views_videos = df_videos['views'].sum()
            st.sidebar.metric("👁️ Views Totais", formatar_numero(total_views_videos))
    
    # Informações do sistema
    st.sidebar.divider()
    st.sidebar.markdown("### ⚙️ Informações do Sistema")
    
    # Ambiente
    ambiente = "🚀 Produção" if IS_PRODUCTION else "🏠 Local"
    st.sidebar.markdown(f"**Ambiente:** {ambiente}")
    
    # Tamanho do banco
    if os.path.exists(DB_PATH):
        tamanho_db = os.path.getsize(DB_PATH) / (1024 * 1024)  # MB
        st.sidebar.metric("💾 Tamanho do Banco", f"{tamanho_db:.1f} MB")
    
    # Cache TTL
    st.sidebar.markdown(f"**🔄 Cache TTL:** {CACHE_TTL//60} min")
    
    # Informações de carregamento
    if 'total_videos_banco' in st.session_state:
        total_banco = st.session_state['total_videos_banco']
        carregados = st.session_state.get('videos_carregados', 0)
        
        if carregados < total_banco:
            st.sidebar.warning(f"⚠️ {carregados:,}/{total_banco:,} vídeos carregados")
        else:
            st.sidebar.success(f"✅ Todos os {total_banco:,} vídeos carregados")
    
    # Controles de cache
    st.sidebar.divider()
    st.sidebar.markdown("### 🔄 Controles")
    
    if st.sidebar.button("🔄 Recarregar Dados", help="Limpa o cache e recarrega dados do banco"):
        st.cache_data.clear()
        st.rerun()
    
    # Informações sobre as funcionalidades
    st.sidebar.divider()
    st.sidebar.markdown("### ℹ️ Como Funciona")
    
    with st.sidebar.expander("📊 Fórmulas de Engajamento Reais:"):
        st.markdown("""
        **🎵 TikTok:**
        `(Curtidas + Comentários + Shares) / Views × 100`
        
        **📺 YouTube:**
        `(Curtidas + Comentários) / Views × 100`
        
        **📸 Instagram:**
        `(Curtidas + Comentários + Shares) / Views × 100`
        
        **🏆 Score de Performance:**
        - 50% Taxa de Engajamento Real
        - 30% Volume de Alcance  
        - 20% Consistência (Views/Vídeo)
        """)
    
    with st.sidebar.expander("📋 O que este dashboard oferece:"):
        st.markdown("""
        **👥 Usuários:**
        - Todos os usuários (ativos e inativos)
        - Rankings com fórmulas reais das redes
        - Análises individuais completas
        
        **🎬 Vídeos:**
        - Todos os vídeos do banco
        - Links diretos quando disponíveis
        - Engajamento calculado por plataforma
        
        **🔗 Gestão de Contas:**
        - Identificador automático de links
        - Detecção de plataforma e dono
        - Gestão completa de contas por usuário
        - Verificação no banco de dados
        
        **📊 Análises:**
        - Métricas oficiais de cada rede
        - Comparações precisas
        - Insights baseados em dados reais
        
        **🎯 Controles:**
        - Escolha quantos mostrar
        - Incluir/excluir inativos
        - Filtros por plataforma específica
        """)
    
    # Nova aba para explicar as métricas
    if st.sidebar.button("📖 Ver Explicação Completa das Métricas"):
        st.session_state['mostrar_explicacao'] = True
    
    # Mostrar explicação se solicitado
    if st.session_state.get('mostrar_explicacao', False):
        with st.expander("📖 Explicação Completa das Métricas", expanded=True):
            st.markdown("""
            ## 🧮 Como São Calculadas as Métricas (Fórmulas Reais)
            
            ### 📈 Taxa de Engajamento por Plataforma:
            
            **🎵 TikTok:**
            ```
            Taxa = (Curtidas + Comentários + Compartilhamentos) / Views × 100
            ```
            - TikTok valoriza **todas as interações** igualmente
            - Taxa boa: 3-9% | Excelente: 9%+
            
            **📺 YouTube:**
            ```
            Taxa = (Curtidas + Comentários) / Views × 100
            ```
            - YouTube **não conta shares** da mesma forma
            - Taxa boa: 2-5% | Excelente: 5%+
            
            **📸 Instagram:**
            ```
            Taxa = (Curtidas + Comentários + Compartilhamentos) / Views × 100
            ```
            - Similar ao TikTok, mas Instagram usa "alcance"
            - Taxa boa: 1-3% | Excelente: 3%+
            
            ### 🏆 Score de Performance (0-100):
            
            **1. Engajamento (50 pontos máx):**
            ```
            Pontos = Taxa de Engajamento × 5 (máx 50)
            ```
            - 10% engajamento = 50 pontos (máximo)
            - 5% engajamento = 25 pontos
            
            **2. Volume (30 pontos máx):**
            ```
            Pontos = log(Views + 1) × 3 (máx 30)
            ```
            - Usa logaritmo para não favorecer apenas "virais"
            - 100K views ≈ 30 pontos (máximo)
            
            **3. Consistência (20 pontos máx):**
            ```
            Pontos = (Views / Vídeos) × 0.002 (máx 20)
            ```
            - Média de 10K views/vídeo = 20 pontos
            - Recompensa quem mantém qualidade
            
            ### 🎯 Categorias Finais:
            - 🏆 **Elite (80-100):** Performance excepcional
            - 🥇 **Expert (60-79):** Muito bom
            - 🥈 **Avançado (40-59):** Bom
            - 🥉 **Intermediário (20-39):** Regular
            - 🌱 **Iniciante (1-19):** Começando
            - 😴 **Inativo (0):** Sem dados
            
            ### ✅ Por Que Estas Fórmulas São Melhores:
            1. **São as fórmulas reais** que cada rede social usa
            2. **Considera a plataforma principal** do criador
            3. **Mais justa** - pequenos criadores podem ter score alto
            4. **Focada no engajamento** - o que realmente importa
            """)
            
            if st.button("❌ Fechar Explicação"):
                st.session_state['mostrar_explicacao'] = False
    
    # Exibir página selecionada
    try:
        if pagina_selecionada == "📊 Dashboard Executivo":
            pagina_dashboard_executivo(df_usuarios)
        elif pagina_selecionada == "🏆 Rankings Completos":
            pagina_rankings_completos(df_usuarios)
        elif pagina_selecionada == "👤 Análise Individual":
            pagina_analise_usuario_avancada(df_usuarios)
        elif pagina_selecionada == "🎬 Vídeos Completos":
            pagina_videos_completa(df_videos)
        elif pagina_selecionada == "🔗 Gestão de Contas":
            pagina_gestao_contas(df_videos, df_usuarios)
            
    except TypeError as e:
        if "unsupported operand type" in str(e):
            st.error("❌ Erro de tipo de dados detectado!")
            st.warning("⚠️ Alguns dados no banco podem ter tipos incompatíveis.")
            st.info("💡 **Soluções específicas:**")
            st.info("1. Clique em 'Recarregar Dados' na sidebar")
            st.info("2. Verifique se há valores não-numéricos em colunas numéricas")
            st.info("3. Confirme se as colunas de views, likes, etc. são números")
            
            with st.expander("🔍 Detalhes técnicos"):
                st.code(str(e))
                st.markdown("**Causa provável:** Tentativa de operação matemática com dados categóricos ou texto")
        else:
            st.error(f"❌ Erro de tipo: {str(e)}")
            st.info("💡 Tente recarregar os dados ou verificar a estrutura do banco.")
            
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        st.info("💡 Tente recarregar os dados ou verificar a conexão com o banco.")
        
        with st.expander("🔍 Detalhes técnicos do erro"):
            st.code(str(e))
            st.markdown("**🛠️ Possíveis soluções:**")
            st.markdown("1. Clique em 'Recarregar Dados' na sidebar")
            st.markdown("2. Verifique se o banco de dados não está corrompido")
            st.markdown("3. Confirme se as tabelas necessárias existem")
            st.markdown("4. Verifique se as colunas têm os nomes e tipos corretos")
            
            if IS_PRODUCTION:
                st.error("🚨 **ERRO EM PRODUÇÃO DETECTADO!**")
                st.markdown("**🔧 Ações de emergência:**")
                st.markdown("- Verificar logs do servidor imediatamente")
                st.markdown("- Considerar rollback para versão estável")
                st.markdown("- Notificar equipe de desenvolvimento")
    
    # Footer informativo
    st.sidebar.divider()
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: #666; font-size: 0.8em;">
        <strong>🚀 TrendX Analytics</strong><br>
        📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br>
        {'🚀 Ambiente: Produção' if IS_PRODUCTION else '🏠 Ambiente: Local'}<br>
        ⚡ Métricas Reais das Redes Sociais<br>
        🔗 Gestão Completa de Contas<br>
        💾 Banco: {DB_PATH}<br>
        🎯 Fórmulas Oficiais: TikTok, YouTube, Instagram<br>
        🔄 Cache: {CACHE_TTL//60} min
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()