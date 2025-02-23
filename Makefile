TARGET = memSim

SOURCE = memSim.py

all: $(TARGET)

$(TARGET): $(SOURCE)
	@echo "#!/usr/bin/env python3" > $(TARGET)
	@cat $(SOURCE) >> $(TARGET)
	@chmod +x $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all clean