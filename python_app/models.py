class Product(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.IntegerField()

    class Meta:
        db_table = 'productos'

    def _str_(self):
        return f"{self.nombre} - Precio: {self.precio} - Cantidad en stock: {self.cantidad_stock}"