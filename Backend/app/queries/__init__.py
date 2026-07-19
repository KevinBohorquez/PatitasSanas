# app/queries
"""
Capa de consultas de lectura (read models).

Aquí viven los ensamblados multi-tabla (JOINs, subconsultas y proyecciones para
la vista) que NO son persistencia de una sola entidad y por tanto no pertenecen
a una clase CRUD. Cada función sirve a una consulta de lectura concreta.
"""
