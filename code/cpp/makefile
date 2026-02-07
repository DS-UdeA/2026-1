# --- Configuración ---
CXX      := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -pedantic
LDFLAGS  :=

SRC_DIR  := src
DATA_DIR := data
BIN_DIR  := bin

# Detecta todos los .cpp en src/
SOURCES  := $(wildcard $(SRC_DIR)/*.cpp)

# Ejecutables bin/<nombre> a partir de src/<nombre>.cpp
TARGETS  := $(patsubst $(SRC_DIR)/%.cpp,$(BIN_DIR)/%,$(SOURCES))

# Copia todos los archivos de data/ a bin/
DATA_FILES := $(wildcard $(DATA_DIR)/*)
DATA_COPY  := $(patsubst $(DATA_DIR)/%,$(BIN_DIR)/%,$(DATA_FILES))

.PHONY: all clean list help data
all: $(BIN_DIR) $(TARGETS) data

# Crea bin/ si no existe
$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Compila cada programa: src/foo.cpp -> bin/foo
$(BIN_DIR)/%: $(SRC_DIR)/%.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

# Copia data/* a bin/*
data: $(BIN_DIR) $(DATA_COPY)

$(BIN_DIR)/%: $(DATA_DIR)/% | $(BIN_DIR)
	@cp -f $< $@

# Lista fuentes, ejecutables y archivos de datos
list:
	@echo "Fuentes (src/*.cpp):"
	@printf "  %s\n" $(SOURCES)
	@echo "Ejecutables (bin/*):"
	@printf "  %s\n" $(TARGETS)
	@echo "Datos a copiar (data/* -> bin/*):"
	@printf "  %s\n" $(DATA_COPY)

# Limpia bin/
clean:
	@rm -rf $(BIN_DIR)

help:
	@echo "Uso:"
	@echo "  make / make all   -> compila src/*.cpp en bin/ y copia data/* a bin/"
	@echo "  make data         -> solo copia data/* a bin/"
	@echo "  make list         -> muestra lo detectado"
	@echo "  make clean        -> borra bin/"
	@echo ""
	@echo "Ejecutar un programa:"
	@echo "  ./bin/<nombre>"

# Ejecuta un programa: make run-foo -> ./bin/foo
run-%: all
	@./$(BIN_DIR)/$*
