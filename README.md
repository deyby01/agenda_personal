# Mi Agenda Personal (Proyecto Django)

Una aplicación web completa desarrollada con Django para la gestión de tareas y proyectos personales, con un sistema de autenticación de usuarios robusto y una interfaz responsiva construida con Bootstrap 5.

**Visita la aplicación en producción:** [https://deyby01.pythonanywhere.com/](https://deyby01.pythonanywhere.com/)

---

Este proyecto fue desarrollado como parte de mi portafolio para demostrar mis habilidades en el desarrollo backend con Django y la construcción de aplicaciones web full-stack. La aplicación permite a los usuarios registrarse, iniciar sesión y gestionar su propia agenda personal, organizando tareas diarias/semanales y proyectos a largo plazo.

El objetivo era construir una aplicación funcional, segura y desplegada en un entorno de producción, cubriendo todo el ciclo de vida del desarrollo web, esto me permitio aprender nuevas cosas a travez del camino y aunque no lo hice 100% solo ya que fue estruturado mediante un aprendizaje independiente, aun sigo aprendiendo como funciona en su totalidad, cabe recalcar que el frontend lo desarrolle siguiendo las instrucciones de la ruta de este proyecto.

## Características Principales

* **Autenticación de Usuarios Completa:**
    * Registro de nuevos usuarios (con campos personalizados como nombre y email).
    * Inicio de sesión y cierre de sesión seguro (con protección CSRF).
    * Restablecimiento de contraseña a través de correo electrónico(Esta parte aun no esta desarrollada para envio de correos ya que aun tengo que aprender a como hacerlo).
    * Cambio de contraseña para usuarios autenticados.
    * Protección de vistas para que cada usuario solo pueda acceder a su propia información.
* **Gestión de Tareas (CRUD Completo):**
    * Crear, leer, actualizar y eliminar tareas.
    * Asignar título, descripción, tiempo estimado y fecha de realización.
    * Marcar tareas como completadas.
* **Gestión de Proyectos (CRUD Completo):**
    * Crear, leer, actualizar y eliminar proyectos a largo plazo.
    * Asignar nombre, descripción, fechas estimadas y estado (Planificado, En Curso, etc.).
* **Vista de Agenda Semanal Interactiva:**
    * Visualización de tareas organizadas por día de la semana.
    * Navegación para ver semanas anteriores y siguientes.
    * Sección dedicada a los proyectos activos durante la semana visible.
* **Interfaz Responsiva:**
    * Construida con Bootstrap 5, asegurando una buena experiencia de usuario en dispositivos de escritorio, tablets y móviles.
* **Despliegue en Producción:**
    * La aplicación está desplegada en PythonAnywhere, utilizando Gunicorn como servidor WSGI y una base de datos MySQL.

## Tecnologías Utilizadas

* **Backend:** Python, Django
* **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript 
* **Base de Datos:** SQLite (para desarrollo local), MySQL (para producción)
* **Servidor de Aplicación WSGI:** Gunicorn
* **Plataforma de Despliegue:** PythonAnywhere
* **Control de Versiones:** Git, GitHub

## Autor

* **Deyby Camacho**
* **LinkedIn:** [[Deyby Camacho](https://www.linkedin.com/in/deyby-camacho-piedrahita-01341b238/)] 

---