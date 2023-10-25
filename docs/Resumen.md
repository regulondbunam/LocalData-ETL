# Manejo de datos locales (Evidencias)



- Obtener IDs de evidencias desde la base de datos de RegulonDBIdentifiers.

- Obtener el Dataframe del documento Excel (EvidenceCatalog)
- Para cada Evidence en el Catalogo
  - Se mapea un objeto Diccionario con las columnas del documento excel que se han definido para cada propiedad.
  - Se revisa si la evidencia es de tipo `rule` `update` o `new`
    - Si es `rule` se genera las reglas correspondientes
    - Si es `update` se agrega la evidence a la lista de evidences a actualizar
    - Si es `new` se agrega la evidence a la lista de evidences nuevas
  - La lista de nuevas evidences 
    - Se verifica que tengan _id y que no sean de categoria cross validation
    - Se le agrega su ID correspondiente segun su Code 

