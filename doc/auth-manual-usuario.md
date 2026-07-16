# Manual de usuario — Autenticación y roles

## Iniciar sesión

1. Entra a la app; si no tienes sesión, te lleva automáticamente a `/login`.
2. Escribe tu **usuario o correo** y tu contraseña. Presiona "Iniciar sesión".
3. Si es tu primer ingreso (o un administrador te reseteó la contraseña), el sistema te pedirá **cambiarla obligatoriamente** antes de dejarte usar el resto de la app.

Si escribes mal la contraseña varias veces, tu cuenta se bloquea temporalmente unos minutos (el bloqueo crece si sigues intentando). El mensaje de error es el mismo si el usuario no existe, la contraseña es incorrecta, o la cuenta está desactivada — por seguridad, no se distingue cuál fue el caso.

## Cambiar tu contraseña

Ve a **Mi Perfil** (ícono en la barra lateral) → sección "Cambiar contraseña". Necesitas tu contraseña actual, la nueva (mínimo 10 caracteres, con letras y números, no puede ser igual a tu usuario) y confirmarla. Tu sesión actual sigue activa después del cambio; las demás sesiones abiertas (si iniciaste sesión en otro dispositivo) se cierran.

## Qué ves según tu rol

| Rol | Ves en la barra lateral | Puedes hacer |
|---|---|---|
| **Superadministrador** | Todo | Gestionar administradores y creadores, ver el dashboard completo, configuración del sistema |
| **Administrador** | Todo excepto configuración de superadmin | Gestionar creadores, marcas, tickets de cualquier creador, y usuarios de rol Creador |
| **Creador** | Inicio, Transacciones, Mi Perfil | Ver y subir **solo tus propios** tickets; ver tu presupuesto en Mi Perfil |

Si entras a una URL que tu rol no puede ver, te muestra una página de "Acceso no autorizado" (no un error).

---

## Para Superadmin y Administradores: gestión de usuarios

En **Administración → Usuarios**:

- **Crear usuario**: botón "Nuevo Usuario". Si el rol es "Creador", debes vincularlo a un Creador ya existente (créalo primero en la pestaña "Creadores" si hace falta). Si no escribes una contraseña, el sistema genera una temporal — anótala, se muestra una sola vez.
- **Resetear contraseña**: genera una nueva contraseña temporal para ese usuario (debe cambiarla en su próximo login). También se muestra una sola vez — compártela por un canal seguro (no por correo sin cifrar ni chat público).
- **Activar/Desactivar**: una cuenta desactivada no puede iniciar sesión. Para desactivar **tu propia cuenta de administrador**, el sistema te pide escribir tu usuario como confirmación, para evitar un bloqueo accidental.

Un administrador **no puede** crear, ver ni editar a otro administrador ni al superadmin — solo el superadmin gestiona administradores. La cuenta superadmin no se puede desactivar ni degradar desde ningún lugar de la app (es intencional: es la única cuenta de ese tipo).

## Para Creadores: tu presupuesto y tickets

- **Mi Perfil** muestra tu presupuesto inicial, lo gastado y lo restante.
- **Nuevo Ticket** (botón naranja de la barra lateral): tu nombre ya viene preseleccionado y no se puede cambiar — solo puedes registrar gastos a tu propio nombre.
- **Transacciones** muestra únicamente tus propios tickets, aunque uses el buscador.

## Si perdiste el acceso

- **Olvidaste tu contraseña (rol Creador o Administrador)**: pide a un administrador o al superadmin que te haga un reset desde Administración → Usuarios.
- **El superadmin perdió su contraseña y no hay otra cuenta con acceso**: esto requiere acceso al servidor (no se puede resolver desde la app, a propósito — la cuenta superadmin es inmutable por API). Desde `backend/`, ejecutar:
  ```
  python reset_superadmin_password.py --password "NuevaClaveSegura123!"
  ```
  Esto resetea la contraseña directamente en la base de datos y obliga a cambiarla en el siguiente login.

---

## Para desarrolladores: correr las pruebas

**Suite pytest** (matriz de permisos, login, tokens — usa su propia base de datos de prueba, nunca `presupuesto.db`):
```
cd backend
python -m pytest
```

**Suite E2E (Playwright)** — requiere un backend y un frontend dedicados a pruebas, con una base de datos separada, para no interferir con tu sesión de desarrollo normal en el puerto 8000/5173:
```
# Terminal 1 — backend de pruebas con su propia DB
cd backend
python seed_auth.py --username superadmin --email superadmin@e2e.grupo-ortiz.com --password "SuperClaveE2E123!" 
# (usar DATABASE_URL=sqlite:///./test_e2e.db antes de este comando y del siguiente)
JWT_SECRET_KEY=e2e-test-secret-0123456789abcdef ENV=development DATABASE_URL=sqlite:///./test_e2e.db CORS_ORIGINS=http://127.0.0.1:5175 python -m uvicorn app.main:app --host 127.0.0.1 --port 8793

# Terminal 2 — frontend apuntando a ese backend
cd frontend
VITE_BACKEND_PORT=8793 npx vite --host 127.0.0.1 --port 5175

# Terminal 3 — la suite
cd frontend
E2E_SUPERADMIN_PASSWORD="SuperClaveE2E123!" E2E_BASE_URL="http://127.0.0.1:5175" npx playwright test
```
Borra `backend/test_e2e.db` antes de repetir el flujo completo desde cero (el superadmin es idempotente, pero los usuarios/creadores que crea la prueba no lo son entre corridas con la misma base).
