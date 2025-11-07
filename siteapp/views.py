from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Usuarios

# ---------- helpers ----------
def _slugify_username(base: str) -> str:
    """
    Gera um username "amigável" a partir de um texto (ex.: prefixo de e-mail),
    garantindo que só tenha letras/números/._- e minúsculas.
    """
    import re
    s = (base or "").strip().lower()
    s = s.split("@")[0] if "@" in s else s
    s = re.sub(r"[^a-z0-9._-]+", "", s)
    return s or "user"

def _unique_username(candidate: str) -> str:
    """
    Garante unicidade do username. Se já existir, adiciona sufixos numéricos.
    """
    base = candidate
    if not User.objects.filter(username__iexact=candidate).exists():
        return candidate
    i = 1
    while True:
        cand = f"{base}{i}"
        if not User.objects.filter(username__iexact=cand).exists():
            return cand
        i += 1

# =========================
# Auth
# =========================
def login_view(request):
    """
    Login flexível: aceita 'usuário OU e-mail' no mesmo campo.
    """
    if request.method == "POST":
        login_input = (request.POST.get("username") or "").strip()  # pode ser username OU e-mail
        password    = request.POST.get("password") or ""

        if not login_input or not password:
            messages.error(request, "Preencha usuário/e-mail e senha.")
            return render(request, "siteapp/login.html")

        # 1) Tenta autenticar diretamente como username
        user = authenticate(request, username=login_input, password=password)
        if user is not None:
            login(request, user)
            return redirect("usuarios")

        # 2) Se falhou, tenta achar por e-mail e autenticar usando o username real
        try:
            u = User.objects.get(email__iexact=login_input)
            user = authenticate(request, username=u.username, password=password)
            if user is not None:
                login(request, user)
                return redirect("usuarios")
        except User.DoesNotExist:
            u = None

        # Mensagens de diagnóstico amigáveis (dev). Em produção, unifique.
        if u is None:
            # Pode ser que o login_input seja um username inexistente OU e-mail inexistente
            try:
                User.objects.get(username__iexact=login_input)
                # username existe mas senha incorreta
                messages.error(request, "Senha incorreta.")
            except User.DoesNotExist:
                messages.error(request, "Usuário/E-mail não encontrado.")
        else:
            messages.error(request, "Senha incorreta.")

        return render(request, "siteapp/login.html")

    return render(request, "siteapp/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    """
    Cadastro modo livre:
    - Username opcional (gera a partir do e-mail se vier vazio).
    - Senha sem validadores rígidos (basta existir).
    - Faz login automático após criar.
    """
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email    = (request.POST.get("email") or "").strip() or None
        pwd1     = request.POST.get("password1") or ""
        pwd2     = request.POST.get("password2") or ""

        # Regras mínimas para não quebrar:
        if not pwd1 or not pwd2:
            messages.error(request, "Informe e confirme a senha.")
            return render(request, "siteapp/register.html")

        if pwd1 != pwd2:
            messages.error(request, "As senhas não conferem.")
            return render(request, "siteapp/register.html")

        # Username permissivo:
        # - se veio preenchido, usa (desde que único);
        # - se veio vazio mas há e-mail, gera do e-mail;
        # - se os dois vierem vazios, cria "user", "user1", etc (não recomendado, mas permitido).
        if username:
            base = _slugify_username(username)
        elif email:
            base = _slugify_username(email)
        else:
            base = "user"

        username_final = _unique_username(base)

        # Evita e-mail duplicado se o e-mail foi informado (opcional — pode comentar se quiser permitir repetido).
        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Já existe uma conta com este e-mail.")
            return render(request, "siteapp/register.html")

        try:
            user = User.objects.create_user(username=username_final, email=email, password=pwd1)
            # Sem privilégios administrativos por padrão
            user.is_staff = False
            user.is_superuser = False
            user.save()

            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("usuarios")

        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {e}")
            return render(request, "siteapp/register.html")

    # GET → mostra o formulário
    return render(request, "siteapp/register.html")


# =========================
# App: CRUD de Usuarios
# =========================
@login_required
def usuarios(request):
    lista = Usuarios.objects.all().order_by("id_usuario")
    return render(request, "siteapp/usuarios_list.html", {"usuarios": lista})


@login_required
def usuario_novo(request):
    if request.method == "POST":
        campos = ["nome", "idade", "email", "telefone", "cep", "logradouro", "bairro", "cidade", "uf"]
        data = {c: (request.POST.get(c, "").strip() or None) for c in campos}

        if not data["nome"]:
            messages.error(request, "Informe ao menos o nome.")
            return render(request, "siteapp/usuarios_form.html", {"editar": False, "dados": data})

        if data["idade"]:
            try:
                data["idade"] = int(data["idade"])
            except ValueError:
                messages.error(request, "Idade inválida.")
                return render(request, "siteapp/usuarios_form.html", {"editar": False, "dados": data})

        Usuarios.objects.create(**data)
        messages.success(request, "Usuário cadastrado com sucesso!")
        return redirect("usuarios")

    return render(request, "siteapp/usuarios_form.html", {"editar": False})


@login_required
def usuario_editar(request, pk):
    u = get_object_or_404(Usuarios, pk=pk)

    if request.method == "POST":
        campos = ["nome", "idade", "email", "telefone", "cep", "logradouro", "bairro", "cidade", "uf"]
        for c in campos:
            setattr(u, c, (request.POST.get(c, "").strip() or None))

        if not u.nome:
            messages.error(request, "Informe ao menos o nome.")
            return render(request, "siteapp/usuarios_form.html", {"editar": True, "u": u})

        if u.idade:
            try:
                u.idade = int(u.idade)
            except ValueError:
                messages.error(request, "Idade inválida.")
                return render(request, "siteapp/usuarios_form.html", {"editar": True, "u": u})

        u.save()
        messages.success(request, "Usuário atualizado com sucesso!")
        return redirect("usuarios")

    return render(request, "siteapp/usuarios_form.html", {"editar": True, "u": u})


@login_required
def usuario_excluir(request, pk):
    u = get_object_or_404(Usuarios, pk=pk)
    if request.method == "POST":
        u.delete()
        messages.success(request, "Usuário excluído.")
        return redirect("usuarios")
    return render(request, "siteapp/usuario_confirm_delete.html", {"u": u})
