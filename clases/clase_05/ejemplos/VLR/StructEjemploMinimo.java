// =============================================================================
// Laboratorio de Estructuras de Datos - UdeA
// Tema: Conceptos Previos — Equivalente Java del ejemplo mínimo de struct
// Sección: 0.3 / 0.4 del README de la carpeta VLR
// =============================================================================
//
// Equivalente Java del script struct_ejemplo_minimo.py.
// Usa java.nio.ByteBuffer para empaquetar y desempaquetar valores binarios,
// que es el análogo directo de struct.pack / struct.unpack en Python.
//
// Compilar y ejecutar:
//   javac StructEjemploMinimo.java
//   java  StructEjemploMinimo
// =============================================================================

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class StructEjemploMinimo {

    public static void main(String[] args) {

        System.out.println("=".repeat(60));
        System.out.println("  Ejemplo mínimo — ByteBuffer (equivalente Java de struct)");
        System.out.println("=".repeat(60));

        // ---------------------------------------------------------------------
        // PASO 1 — Empaquetar  (≡ struct.pack('>HH', offset, length))
        // ---------------------------------------------------------------------
        // Una entrada del slot directory ocupa 4 bytes:
        //   offset (2B, uint16 big-endian) + length (2B, uint16 big-endian)
        //
        // En Java los short son de 16 bits con signo, pero los valores que
        // usamos (0–65535) caben sin problema. Se usa (short) para el cast.

        int offset = 215;   // el registro comienza en el byte 215 de la página
        int length = 41;    // el registro ocupa 41 bytes

        // allocate(4): 2 bytes para offset + 2 bytes para length
        ByteBuffer packed = ByteBuffer.allocate(4);
        packed.order(ByteOrder.BIG_ENDIAN);  // equivalente al prefijo '>' en Python
        packed.putShort((short) offset);
        packed.putShort((short) length);

        System.out.println("\n── Paso 1: empaquetar ──────────────────────────────────");
        System.out.printf("  offset = %d  →  hex: 0x%04X%n", offset, offset);
        System.out.printf("  length = %d   →  hex: 0x%04X%n", length, length);
        System.out.println("  ByteBuffer.putShort(offset) + putShort(length)");
        System.out.printf("  Resultado  : %s%n", toHexString(packed.array()));
        System.out.printf("  Tamaño     : %d bytes%n", packed.capacity());

        // ---------------------------------------------------------------------
        // PASO 2 — Inspección byte a byte
        // ---------------------------------------------------------------------
        // 215 decimal = 0x00D7
        //   Big-endian:    byte[0]=0x00, byte[1]=0xD7   ← MSB primero
        // 41 decimal = 0x0029
        //   Big-endian:    byte[2]=0x00, byte[3]=0x29

        System.out.println("\n── Paso 2: inspección byte a byte ─────────────────────");
        byte[] raw = packed.array();
        for (int i = 0; i < raw.length; i++) {
            // & 0xFF convierte el byte con signo de Java a un int sin signo (0-255)
            int unsigned = raw[i] & 0xFF;
            System.out.printf("  byte[%d] = 0x%02X  (%3d decimal)%n", i, unsigned, unsigned);
        }
        System.out.println();
        System.out.println("  Nota: 0xD7 = 215. Big-endian escribe 0x00 (MSB) antes");
        System.out.println("  que 0xD7 (LSB). En little-endian sería al revés: D7 00.");

        // ---------------------------------------------------------------------
        // PASO 3 — Desempaquetar  (≡ struct.unpack('>HH', packed))
        // ---------------------------------------------------------------------
        // rewind() mueve el cursor de vuelta al byte 0 antes de leer.

        packed.rewind();
        int recoveredOffset = Short.toUnsignedInt(packed.getShort());
        int recoveredLength = Short.toUnsignedInt(packed.getShort());

        System.out.println("\n── Paso 3: desempaquetar ───────────────────────────────");
        System.out.printf("  offset recuperado : %d%n", recoveredOffset);
        System.out.printf("  length recuperado : %d%n", recoveredLength);

        assert recoveredOffset == offset : "¡El offset no coincide!";
        assert recoveredLength == length : "¡El length no coincide!";
        System.out.println("  Round-trip OK ✓");

        // ---------------------------------------------------------------------
        // PASO 4 — pack_into / unpack_from sobre un buffer de página
        //          (≡ struct.pack_into / struct.unpack_from sobre bytearray)
        // ---------------------------------------------------------------------
        // Aquí simulamos escribir un slot en una "página" de 256 bytes,
        // igual que en los scripts v6 y v7 del laboratorio.

        System.out.println("\n── Paso 4: escribir y leer en buffer de página ────────");
        ByteBuffer page = ByteBuffer.allocate(256);
        page.order(ByteOrder.BIG_ENDIAN);

        int SLOT_0_POS = 8;   // el primer slot empieza en el byte 8 (tras el header)

        System.out.printf("  page antes  : %s  (bytes 8-11, todos en 0x00)%n",
                toHexString(page.array(), SLOT_0_POS, 4));

        // Posicionar el cursor y escribir
        page.position(SLOT_0_POS);
        page.putShort((short) offset);
        page.putShort((short) length);

        System.out.printf("  page después: %s  (bytes 8-11 tras putShort x2)%n",
                toHexString(page.array(), SLOT_0_POS, 4));

        // Leer de vuelta desde la posición 8
        page.position(SLOT_0_POS);
        int readOffset = Short.toUnsignedInt(page.getShort());
        int readLength = Short.toUnsignedInt(page.getShort());

        System.out.printf("  getShort x2 → offset=%d, length=%d%n", readOffset, readLength);

        assert readOffset == offset;
        assert readLength == length;
        System.out.println("  Round-trip sobre buffer de página OK ✓");

        // ---------------------------------------------------------------------
        // EXTRA — comparación big-endian vs little-endian
        // ---------------------------------------------------------------------

        System.out.println("\n── Extra: big-endian vs little-endian ─────────────────");

        ByteBuffer be = ByteBuffer.allocate(4).order(ByteOrder.BIG_ENDIAN);
        be.putShort((short) offset).putShort((short) length);

        ByteBuffer le = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN);
        le.putShort((short) offset).putShort((short) length);

        System.out.printf("  Big-endian    BIG_ENDIAN   : %s   ← 0x00 primero (MSB)%n",
                toHexString(be.array()));
        System.out.printf("  Little-endian LITTLE_ENDIAN: %s   ← 0xD7 primero (LSB)%n",
                toHexString(le.array()));
        System.out.println();
        System.out.println("  Mismo número, mismo tamaño, distinto orden de bytes.");
        System.out.println("  El motor debe usar siempre el mismo orden al leer y escribir.");

        System.out.println("\n" + "=".repeat(60));
        System.out.println("  Fin del ejemplo. Sin errores.");
        System.out.println("=".repeat(60));
    }

    // ── Helpers de formateo ──────────────────────────────────────────────────

    /** Convierte un arreglo de bytes completo a string hex separado por espacios. */
    private static String toHexString(byte[] bytes) {
        return toHexString(bytes, 0, bytes.length);
    }

    /** Convierte un rango de bytes a string hex separado por espacios. */
    private static String toHexString(byte[] bytes, int from, int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = from; i < from + count; i++) {
            if (i > from) sb.append(' ');
            sb.append(String.format("%02x", bytes[i] & 0xFF));
        }
        return sb.toString();
    }
}
