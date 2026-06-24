-- Tabla de clientes: almacena la información personal de los clientes
CREATE TABLE cliente (
  id_cliente INT AUTO_INCREMENT PRIMARY KEY,
  cedula VARCHAR(20) UNIQUE,
  nombres VARCHAR(50),
  apellidos VARCHAR(50),
  telefono VARCHAR(20)
);

-- Tabla de empleados: registra los datos de los trabajadores del restaurante
CREATE TABLE empleado (
  id_empleado INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50),
  cargo VARCHAR(30),
  telefono VARCHAR(20),
  email VARCHAR(50)
);

-- Tabla de mesas: define las mesas físicas del restaurante con número, capacidad y ubicación
CREATE TABLE mesa (
  id_mesa INT AUTO_INCREMENT PRIMARY KEY,
  numero_mesa INT NOT NULL,
  capacidad INT,
  ubicacion VARCHAR(50)
);

-- Tabla de categorías de platos: clasifica los platos (entrada, plato fuerte, bebida, postre)
CREATE TABLE categoria_plato (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  descripcion VARCHAR(50)
);

-- Tabla de platos: almacena los platos del menú y su categoría
CREATE TABLE plato (
  id_plato INT AUTO_INCREMENT PRIMARY KEY,
  id_categoria INT,
  nombre_plato VARCHAR(50),
  FOREIGN KEY (id_categoria) REFERENCES categoria_plato(id_categoria)
);

-- Tabla de pedidos: registra cada pedido realizado por un cliente, atendido por un empleado y opcionalmente asociado a una mesa
CREATE TABLE pedido (
  id_pedido INT AUTO_INCREMENT PRIMARY KEY,
  id_cliente INT,
  id_empleado INT,
  id_mesa INT NULL,
  fecha_pedido DATETIME,
  total DECIMAL(10,2),
  estado VARCHAR(20),
  FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
  FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado),
  FOREIGN KEY (id_mesa) REFERENCES mesa(id_mesa)
);

-- Tabla de detalle de pedido: desglosa los platos incluidos en cada pedido con cantidad y subtotal
CREATE TABLE detalle_pedido (
  id_detalle_pedido INT AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT,
  id_plato INT,
  cantidad INT,
  subtotal DECIMAL(10,2),
  FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
  FOREIGN KEY (id_plato) REFERENCES plato(id_plato)
);

-- Tabla de pagos: registra los pagos asociados a un pedido, con forma de pago, fecha, valor y estado
CREATE TABLE pago (
  id_pago INT AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT,
  forma_pago VARCHAR(20),
  fecha_pago DATETIME,
  valor_pago DECIMAL(10,2),
  estado VARCHAR(20),
  FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido)
);
