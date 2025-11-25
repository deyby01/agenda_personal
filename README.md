# Mi Agenda Personal (Proyecto Django)

Una aplicación web completa desarrollada con Django para la gestión de tareas y proyectos personales, con un sistema de autenticación moderno y una interfaz responsiva construida con Bootstrap 5.

**Visita la aplicación en producción:** [https://deyby01.pythonanywhere.com/](https://deyby01.pythonanywhere.com/)

---

Este proyecto fue desarrollado como parte de mi portafolio para demostrar mis habilidades en el desarrollo backend con Django y la construcción de aplicaciones web full-stack. La aplicación permite a los usuarios registrarse, iniciar sesión (usando su email o su cuenta de Google) y gestionar su propia agenda personal, organizando tareas diarias y proyectos a largo plazo.

El objetivo era construir una aplicación funcional, segura y desplegada en un entorno de producción, cubriendo todo el ciclo de vida del desarrollo web. El proyecto ha sido completamente refactorizado de Vistas Basadas en Funciones a Vistas Basadas en Clases (CBV), siguiendo las mejores prácticas de Django para un código más limpio, escalable y mantenible.

## Características Principales

* **Autenticación Moderna y Segura (con `django-allauth`):**
    * Registro de nuevos usuarios con campos personalizados.
    * Inicio de sesión con **email y contraseña**.
    * Inicio de sesión social con **Google (OAuth2)**.
    * Sistema completo de **restablecimiento de contraseña**.
    * Cambio de contraseña para usuarios autenticados.
    * Protección de vistas para que cada usuario solo pueda acceder a su propia información.

* **Gestión de Tareas (CRUD Completo):**
    * Crear, leer, actualizar y eliminar tareas.
    * Asignar título, descripción, tiempo estimado y fecha de realización.
    * Marcar tareas como completadas con un solo clic.

* **Gestión de Proyectos (CRUD Completo):**
    * Crear, leer, actualizar y eliminar proyectos a largo plazo.
    * Asignar nombre, descripción, fechas estimadas y estado (Planificado, En Curso, etc.).

* **Vista de Agenda Semanal Interactiva:**
    * Visualización de tareas organizadas por día de la semana.
    * Navegación para ver semanas anteriores y siguientes.
    * Sección dedicada a los proyectos activos durante la semana visible.

* **Interfaz Responsiva:**
    * Construida con Bootstrap 5, asegurando una buena experiencia de usuario en dispositivos de escritorio, tablets y móviles.

## API RESTful

- Endpoints versionados bajo `api/v1/` (tasks, projects, notifications).
- Autenticación JWT vía `/api/token/` y `/api/token/refresh/`.
- Documentación generada con **drf-spectacular**:
  - OpenAPI JSON: `/api/schema/`
  - Swagger UI interactivo: `/api/docs/swagger/`
  - ReDoc: `/api/docs/redoc/`

## Mejoras Técnicas Clave

* **Refactorización a Vistas Basadas en Clases (CBV):** Todo el proyecto fue migrado de Vistas Basadas en Funciones (FBV) a CBV, utilizando las vistas genéricas de Django (`ListView`, `CreateView`, `UpdateView`, `DeleteView`, `TemplateView`) para un código más reutilizable, mantenible y escalable.
* **Lógica de Negocio Encapsulada:** La lógica de negocio, como la seguridad de los objetos (asegurando que un usuario solo pueda ver y modificar sus propios datos), se ha implementado de forma robusta en los métodos de las clases (`get_queryset`).
* **Flujo de Trabajo Profesional con Git:** Se utilizó un flujo de trabajo basado en ramas (`feature branches`) para desarrollar nuevas funcionalidades de forma aislada y segura antes de fusionarlas con la rama principal (`main`).

## Tecnologías y Librerías

* **Backend:** Python, Django
* **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
* **Base de Datos:** SQLite (desarrollo), MySQL (producción)
* **Librerías Principales de Django:**
    * `django-allauth` (para autenticación social y local)
    * `django-crispy-forms` y `crispy-bootstrap5` (para renderizado de formularios)
* **Servidor de Aplicación WSGI:** Gunicorn
* **Plataforma de Despliegue:** PythonAnywhere
* **Control de Versiones:** Git, GitHub

## Autor

* **Deyby Camacho**
* **LinkedIn:** [Deyby Camacho Piedrahita](https://www.linkedin.com/in/deyby-camacho-piedrahita-01341b238/)

---