# Laboratorio 1: Control de Versiones con Git y GitHub

## Objetivos

* Familiarizarse con el control de versiones de código fuente mediante el uso de Git.
* Crear su primer repositorio de Git.
* Aprender comandos de Git de gran utilidad que se emplearán a lo largo de todo el curso.
* Crear un repositorio en GitHub y aprender a cargar (push) y descargar (pull) código desde dicho repositorio.

## Requisitos

* Cuenta de GitHub.
* Git instalado (Opcionalmente puede instalar clientes graficos como GitHub Desktop o GitKraken).
* Python 3.10+.
* Editor de código (VS Code recomendado).

## Recomendación antes de empezar

To Do!
* https://learngitbranching.js.org/?locale=es_ES
* https://docs.github.com/es/get-started/using-git/about-git

## Introducción

GitHub es mucho más que un simple lugar para guardar código. Es una plataforma de colaboración que permite a equipos de todos los tamaños trabajar juntos, llevar un control de versiones y construir proyectos de manera ordenada.

El objetivo principal de este laboratorio es facilitar el aprendizaje de GitHub desde sus fundamentos, priorizando la colaboración y el control de versiones. Este espacio está diseñado para quienes no cuentan con experiencia previa, siendo ideal para estudiantes y equipos que desean dar sus primeros pasos en el ecosistema del desarrollo colaborativo.

Durante la práctica, se aprenderá a crear un repositorio, gestionar ramas, realizar cambios e integrar fusiones de código de manera efectiva. Todo esto se llevará a cabo mediante ejercicios prácticos con archivos sencillos de Python, permitiendo al estudiante familiarizarse con el flujo de trabajo técnico de forma clara.

Al finalizar este laboratorio, los participantes habrán consolidado una base sólida para el trabajo en equipo y la gestión de evidencias de sus avances, competencias que son pilares fundamentales para el desempeño en cualquier entorno de desarrollo profesional.

## Manejo de repositorios usando git

[Git](https://en.wikipedia.org/wiki/Git) es un sistema de control de versiones (VCS) diseñado para realizar el seguimiento de los cambios en los diversos archivos de un repositorio determinado. En particular, esta herramienta resulta de gran utilidad para:
* Mantener un registro detallado de las versiones de sus archivos.
* Facilitar el trabajo de forma paralela gracias al concepto de ramas (branches).
* Resguardar la información mediante copias de seguridad en un servidor remoto ([github](https://en.wikipedia.org/wiki/GitHub) o [gitlab](https://en.wikipedia.org/wiki/GitHub) por ejemplo).

La siguiente figura resume el flujo de trabajo empleando repositorios:

![git-overview](git-overview.png)

### Flujo de Trabajo con Git (VCS Workflow)

Para utilizar Git de manera efectiva, es fundamental comprender que el código no se envía directamente al servidor. 

En su lugar, el trabajo transita por un ciclo de estados que permite gestionar versiones de forma organizada y segura. Este flujo se divide en dos entornos principales: el Entorno Local (su computadora) y el Entorno Remoto (el servidor en la nube, como GitHub).

![workflow](workflow.png)

### Áreas de Git

A continuación, se describen las áreas clave representadas en el diagrama anterior:
* **Working Directory (Directorio de Trabajo)**: Es el entorno donde usted interactúa directamente con los archivos del proyecto. Aquí es donde crea, edita o elimina líneas de código en su editor de preferencia.
* **Staging Area (Área de Preparación)**: Actúa como una zona intermedia o "borrador". En esta área, usted selecciona específicamente qué cambios realizados en el directorio de trabajo desea incluir en su próxima versión o "fotografía" del proyecto.  
* **Local Repository (Repositorio Local)**: Es la base de datos interna en su equipo donde Git almacena el historial completo de todas las versiones confirmadas. Una vez que un cambio llega aquí, queda registrado permanentemente en su historial personal.
* **Remote Repository (Repositorio Remoto)**: Es la instancia del proyecto alojada en un servidor externo  (como GitHub o GitLab). Su función principal es servir como punto central de colaboración, permitiendo que otros integrantes del equipo accedan a su código y viceversa.

### Comandos esenciales de Git

Estos son los comandos fundamentales de Git que usted utilizará regularmente para gestionar su código y colaborar con otros.
* **`git add`**: Mueve los cambios desde el directorio de trabajo hacia el área de preparación. Puede añadir archivos específicos o todos los cambios.
* **`git commit`**: Toma los cambios preparados y los guarda de forma permanente en el repositorio local con un mensaje descriptivo.
* **`git push`**: Carga sus confirmaciones (commits) locales a un repositorio remoto, poniéndolas a disposición de otros miembros del equipo.
* **`git pull`**: Descarga los cambios de un repositorio remoto y los integra en su repositorio local.
* **`git checkout`**: Cambia entre ramas o restaura archivos desde una confirmación (commit) específica. También se utiliza para crear nuevas ramas.

La siguiente tabla muestra de manera resumida los comandos que mas se van a utilizar durante este laboratorio:


<table>
<thead>
  <tr>
    <th colspan="2"> Comandos git basicos
  </th>
  </tr>
  </thead>
<tbody>
  <tr>
  <td colspan="2"> <b> Creación de repositorios </b></td>
  <tr>
    <td><code>git config --global user.name "[name]"</code></td>
    <td>Establece el nombre que desea esté anexado a sus transacciones de commit</td>
  </tr>
  <tr>
    <td><code>git config --global user.email "[email address]"</code></td>
    <td>Establece el e-mail que desea esté anexado a sus transacciones de commit</td>
  </tr>
  <tr>
    <td colspan="2"><b> Creación de repositorios</b></td>
  </tr>
  <tr>
    <td><code>git clone [url]</code></td>
    <td>Descarga un proyecto y toda su historia de versión</td>
  </tr>
  <tr>
    <td colspan="2"><b> Creación de repositorios </b></td>
  </tr>
  <tr>
    <td><code>git status</code></td>
    <td>Enumera todos los archivos nuevos o modificados que se deben confirmar</td>
  </tr>
  <tr>
    <td><code>git add [file]</code></td>
    <td>Toma una instantánea del archivo para preparar la versión</td>
  </tr>
  <tr>
    <td><code>git commit -m "[descriptive message]"</code></td>
    <td>Registra las instantáneas del archivo permanentemente en el historial de versión</td>
  </tr>
  <tr>
    <td colspan="2"><b> Creación de repositorios </b></td>
  </tr>
  <tr>
    <td><code>git push [alias] [branch]</code></td>
    <td>Carga todos los commits de la rama local al GitHub</td>
  </tr>
  <tr>
    <td><code>git pull</code></td>
    <td>Descarga el historial del marcador e incorpora cambios</td>
  </tr>
</tbody>
</table>

> [!TIP] 
> Para profundizar mas consulte la pagina **Tips with Git, Bash** ([link](https://www.mit.edu/~amidi/teaching/data-science-tools/study-guide/engineering-productivity-tips/))


En el siguiente [link](https://rogerdudler.github.io/git-guide/index.es.html) se ilustra y explica muy bien lo más necesario.

A continuación, se comparten algunos resúmenes que le pueden servir, el cacharreo va de cuenta suya:

> [!note]
> **Resumen de comandos**: En las siguientes paginas se muestra una lista de comandos utiles para tener a la mano:
> 1. **Git Cheat Sheet** (github) [[link]]([command_memento.pdf](https://training.github.com/downloads/github-git-cheat-sheet.pdf))
> 2. **Git Cheat Sheet** (Roger Dudler) [[link]](https://rogerdudler.github.io/git-guide/files/git_cheat_sheet.pdf)
> 3. **Git Cheat Sheet** (GitLab) [[link]](https://about.gitlab.com/images/press/git-cheat-sheet.pdf)
> 4. **Git Cheat Sheet** (github) [[español]](https://training.github.com/downloads/es_ES/github-git-cheat-sheet.pdf) [[ingles]](https://education.github.com/git-cheat-sheet-education.pdf)

### Resumen grafico de Git

La mejor tener una visión amplia de `git` es a traves del **git cheat sheet** de [Julia Evans](https://x.com/b0rk)

![git](git_julia_evans.png)

## Ejercicio 1 - flujo completo con PR + verificación

### 0. Checklist

Al terminar, debe tener:
- [ ] Repositorio creado con estructura base.
- [ ] Pruebas corriendo localmente (pytest).
- [ ] Un PR creado desde una rama `feature/...` y mergeado a `main`.
- [ ] Evidencia: enlaces al repo y al PR.

### 1. Crear el repositorio en GitHub

1. Crear un repositorio llamado: `lab-github-<tu_usuario>`
   
   ![fig1_1](images/exercises/fig1_1.png)

2. Inicialice el repositorio con:
   - **Choose visibility**: Public 
   - **Add README**: On
   - **Add .gitignore**: Python
   - **Add license**: Licencia MIT (opcional)

   ![fig1_2](images/exercises/fig1_2.png) 

> ✅ **Checkpoint 1 (resultado esperado)**
> 
> En GitHub se ve el repositorio con `README.md` y `.gitignore`.
> 
> ![fig1_3](images/exercises/fig1_3.png) 

---

### 2. Clonar y preparar entorno local

Para clonar en el entorno local, lo primero que se debe realizar es abrir la terminal del git:

![fig1_4](images/exercises/fig1_4.png) 

Una vez que esta se encuentra abierta, estará lista para recibir comandos:

![fig1_5](images/exercises/fig1_5.png) 

El siguiente paso, es definir un lugar en el sistema de archivos local en el cual descargar el repositorio. En nuestro caso, se eligió en la ruta: `C:\Users\Usuario\Documents\UdeA\2026-1\repos\labs-repos`. La siguiente imagen muestra este directorio vacio:

![fig1_5](images/exercises/fig1_7.png) 

Mediante el uso del comando `cd` nos ubicamos en esta ruta y mediante el comando `pwd` verificamos que esta ruta, sea la corresponiente al directorio actual:

```
cd <path>
pwd
```

![fig1_5](images/exercises/fig1_7_2.png) 

> [!warning]
> Note el formato del path ingresado en la terminal es Linux, el cual es diferente al formato Windows. En nuestro ejemplo quedo el **path** como  ` /c/Users/Usuario/Documents/UdeA/2026-1/repos/labs-repos`

Luego, copie la ruta en la cual se encuentra el repositorio en github:

![fig1_6](images/exercises/fig1_6.png) 

Finalmente, emplee e comando `git clone` para descargar el repositorio:

```
git clone <repo_link>
```

![fig1_7](images/exercises/fig1_7_3.png) 

Si el repositorio se descargo con exito, notara una salida como la de la figura anterior y si observa el sistema de archivos este ya contara con una carpeta cuyo nombre coincide con el del repositorio de github:

![fig1_7](images/exercises/fig1_7_4.png) 

Ingrese ahora a este directorio y verifique su contenido:

```
git clone <dir_repo>
ls -ahl
```

![fig1_8](images/exercises/fig1_8.png) 


Ahora, empleando nuestro editor o IDE favorito podemos abrir el directorio asociado al repositorio (recuerde la ruta)

![fig1_9](images/exercises/fig1_9.png) 


## Referencias

1. https://carpentries-incubator.github.io/open-science-with-r/09-collaborating/index.html
2. https://colab.research.google.com/github/astg606/py_materials/blob/master/git_tutorial/git_and_github.ipynb
3. https://lmu-osc.github.io/Collaborative-RStudio-GitHub/
4. https://learning.nceas.ucsb.edu/2021-11-RRCourse/git-collaboration-and-conflict-management.html
5. https://blog.devgenius.io/git-workflow-complete-guide-for-beginners-with-commands-examples-afcccd50f195
6. https://smartprogramming.in/tutorials/git-and-github/git-add-files-to-staging
7. https://pages.cs.wisc.edu/~lcai64/
8. https://kevinsguides.com/guides/code/devops/file-mgmt/git-github-workflow-branch-merge/