# Constancia fiscal
Programa en Python para validar la seccion "Datos de Identificación del Contribuyente" de una o varias constancia fiscal del SAT,  utilizado mas que nada contadores que requieren validar la informacion que se muestra en el archivo con lo registrado ante el SAT, ya que la información mostrada en el archivo puede estar desactualizado


#¿a que se refiere con validar la información de la constancia fiscal?
  
  El archivo pdf de la constancia fiscal que nos porporciona el sat, no muestra la informacion más actualizada y esto sucede por algun cambio 
  que tramitamos ante el sat y seguimos usando este archivo aun despues del cambio realizado y se puede comprobar comparando la informacion mostrada 
  en el pdf, con la informacion de la url que nos muestra el QR que se encuentra en la misma cosntancia y en varios casos la información no coincide
  
  
#¿Por que hacer este programa?

  si trabajs en una empresa donde tienes que validar no uno si no varias contancias fiscales, esa validacion manual puede conllevar a errores o aumento de 
  tiempo en la actividad por revizar cada constancia.

#¿Que ventajas tiene?

  Aumento de productividad en las validaciones disminucion de tiempo y disminución de errores al realizar las validaciones manualmente.


#¿Que información valida?

  En esta primera version valida los siguientes campos: RFC, CURP, Nombre, Primer apellido, Segundo apellido
 
#¿Como lo hace?  

  En terminos simples:

  1.- se obtiene la informacion de los campos a validar (RFC, CURP, Nombre, Primer apellido, Segundo apellido) del PDF
  2.- se accede a la url que se obtiene del QR de la constancia fiscal y se obtiene los campos a validar (RFC, CURP, Nombre, Primer apellido, Segundo apellido)
  3.- se valida cad campo del PDF Vs url y se verifica si son identicos


#¿como lo uso?

  en este repositorio solo esta el codigo fuente en python para adaptarlo a sus necesidades, para los que no son programadores, se puede acceder a este link para 
  descargarlo y empezar a usarlo.


link para descargar el programa: 


![Formato de constancia fiscal valido](https://github.com/azcue/ConstanciaFiscal/blob/main/constanciaFiscal.png "Formato de constancia fiscal valido")
