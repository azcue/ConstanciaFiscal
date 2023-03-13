# Constancia fiscal
Programa en Python para validar la seccion "Datos de Identificación del Contribuyente" de una o varias constancia fiscal del SAT,  utilizado mas que nada contadores que requieren validar la informacion que se muestra en el archivo con lo registrado ante el SAT, ya que la información mostrada en el archivo puede estar desactualizado


## ¿a que se refiere con validar la información de la constancia fiscal?
  
  El archivo pdf de la constancia fiscal que nos porporciona el sat, no muestra la informacion más actualizada y esto sucede por algun cambio 
  que tramitamos ante el sat y seguimos usando este archivo aun despues del cambio realizado y se puede comprobar comparando la informacion mostrada 
  en el pdf, con la informacion de la url que nos muestra el QR que se encuentra en la misma cosntancia y en varios casos la información no coincide
  
  
## ¿Por que hacer este programa?

  si trabajas con muchas altas de empleado donde tienes que validar no uno si no varias contancias fiscales, esa validacion manual puede conllevar a 
  errores o aumento en el tiempo de la actividad por revizar cada constancia.

## ¿Que ventajas tiene?

  Aumento de productividad en las validaciones, disminucion de tiempo y disminución de errores en las validaciones.


## ¿Que información valida?

  En esta primera versión valida los siguientes campos: RFC, CURP, Nombre, Primer apellido, Segundo apellido
 
## ¿Como lo hace?  

  En terminos simples:

  1.- se obtiene la informacion de los campos a validar (RFC, CURP, Nombre, Primer apellido, Segundo apellido) del PDF
  2.- se accede a la url que se obtiene del QR de la constancia fiscal y se obtiene los campos a validar (RFC, CURP, Nombre, Primer apellido, Segundo apellido)
  3.- se valida cad campo del PDF Vs url y se verifica si son identicos


## ¿como lo uso?

  en este repositorio solo esta el codigo fuente en python para adaptarlo a sus necesidades, para los que no son programadores, se puede acceder a este link para 
  descargarlo y empezar a usarlo:
  
    https://drive.google.com/file/d/1Y9nxFbvkWDvJaPVnPbL7wNzV58A3eZGg/view?usp=sharing

  Una ves descargado solo se debe agregar en la carpeta "files" los archivos que se deben validar pueden existir los archivos pdf o carpetas que contiene 
  uno o mas archivos, concidera que en archivo "config.ini" en el prametro "texto_buscar_archivo_a_comparar" por default especifica que solo validará todos
  los archivos pdf que en su nombre del archivo tengan la palabra "sat", pero se puede cambiar si asi lo desea.
  
  ya que se tenga los archivos a validar y se cumple con la palabra clave que se encuentra en la configuración, ejecutar "valida_constanciaFiscal.exe" 



Formato valido:
<p align="center">
  <img src="https://github.com/azcue/ConstanciaFiscal/blob/main/constanciaFiscal.png" width="50%" heigth="50%">
</p>


