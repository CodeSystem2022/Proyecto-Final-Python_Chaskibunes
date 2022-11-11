/*
 * Los Chaskibunes
 * Trabajo de PSeint a java
 */
package Pseintenjava;

import java.util.Scanner;
import java.io.*;

public class Pseintenjava129 {
	static Scanner entrada = new Scanner(System.in);
	public static void main(String args[]) throws InterruptedException, IOException {
		String m;
		int n;
		do {
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			m = entrada.nextLine();
			System.out.println("                                        CONVERSOR");
			System.out.println("===================================================================================================");
			System.out.println("                                    ¿CUANTO TARDARAS?  ");
			System.out.println("");
			System.out.println(" Indicar medio de trasporte:");
			System.out.println(" 1.A pie    2.Bicibleta    3.Automovil/Motocicleta    4.Barco    5.Avion  6.Tren Electrico  7.Salir");
			n = Integer.parseInt(entrada.nextLine());
			//Menu de opciones, depende que opcion de el usuario 
			switch (n) {
			case 1:
				animacionpie(n);
				apie(n);
				break;
			case 2:
				animacionbici(n);
				enbici(n);
				break;
			case 3:
				animacionauto(n);
				enautomovil(n);
				break;
			case 4:
				animacionbarco(n);
				enbarco(n);
				break;
			case 5:
				animacionavion(n);
				enavion(n);
				break;
			case 6:
				animaciontren(n);
				entren(n);
				break;
			case 7:
				m = "N";
				break;
			default:
				System.out.println("Opcion no valida");//Si el usuario ingresa una opcion inexistente.
			}
			if (!m.equals("N")) {
				System.out.print("¿Desea verificar otra opcion? (Y/N)");
				do {
					m = entrada.nextLine();
				} while (!((m.equals("y") || m.equals("Y") || m.equals("n") || m.equals("N"))));
			}
		} while (!(m.equals("N") || m.equals("n")));
		System.out.println(""); // no hay forma directa de borrar la consola en Java
		System.out.println("");
		System.out.println("  GRACIAS POR ELEGIRNOS COMO SU CONVERSOR");
		System.out.println("  ESPERAMOS QUE LES HALLA SIDO DE UTILIDAD");
		System.out.println("                     ATTE: LOS CHASKIBUNES ");
	}
	// Conversor de unidades de millas o pies a Kilomentros
	public static void convertirunidades(double km, int n) throws IOException {
		double millas;
		double pies;
		int x;
		km = 0;
		System.out.println("Convertir a Kilometros");
		System.out.print("1.Millas   2.Pies");
		x = Integer.parseInt(entrada.nextLine());
		switch (x) {
		case 1:
			System.out.println("---MILLAS---");
			millas = Double.parseDouble(entrada.nextLine());
			km = 1.60934*millas;
			System.out.println(millas+" millas son "+km+" km");
			break;
		case 2:
			System.out.println("---PIES---");
			pies = Double.parseDouble(entrada.nextLine());
			km = 0.0003048*pies;
			System.out.println(pies+" pies son "+km+" km");
			break;
		}
		switch (n) {
		case 1:
			mostrardistancia(km);
			break;
		case 2:
			mostrardistanciabici(km);
			break;
		case 3:
			mostrardistanciaauto(km);
			break;
		case 4:
			mostrardistanciabarco(km);
			break;
		case 5:
			mostrardistanciaavion(km);
			break;
		case 6:
			mostrardistanciatren(km);
			break;
		default:
			System.out.println("ERROR");
		}
	}

	// Mostrar distancia
	public static void mostrardistancia(double km) {
		double q;
		// 13 minutos es el promedo q se tarda en recorre 1km a pie
		q = 13*km;
		System.out.println("Tu timepo a recorrer a pie es de:"+q+" min");
		aguaapie(q);
	}

	// Opcion a pie.
	public static void apie(int n) throws IOException {
		double km;
		String m;
		km = 0;
		System.out.println(""); // no hay forma directa de borrar la consola en Java
		System.out.println(" ---  A PIE  ---");
		System.out.println("");
		System.out.println("        O      ");
		System.out.println("       /|\\     ");
		System.out.println("_______/_\\______");
		System.out.println("");
		System.out.println("Indicar distancia en kilometros a recorrer: ");
		do {
			System.out.print("¿Necesita convertir unidades? (Y/N)");
			m = entrada.nextLine();
		} while (!((m.equals("y") || m.equals("Y") || m.equals("n") || m.equals("N"))));
		System.out.print("Kilometros: ");
		if (m.equals("Y") || m.equals("y")) {
			convertirunidades(km,n);
		} else {
			km = Double.parseDouble(entrada.nextLine());
			mostrardistancia(km);
		}
	}

	// mostrara la distancia en min, en bici
	public static void mostrardistanciabici(double km) {
		double q;
		// 2 minutos es el promedo q se tarda en recorre 1km en bici
		q = 2*km;
		System.out.println("Tu timepo a recorrer en bici es de:"+q+" min");
		aguaabici(q);
	}

	// Opcion en bicicleta
	public static void enbici(int n) throws IOException {
		double km;
		String m;
		km = 0;
		System.out.println(""); // no hay forma directa de borrar la consola en Java
		System.out.println(" ---  EN BICI  ---");
		System.out.println("");
		System.out.println("         o     ");
		System.out.println("         |<} ");
		System.out.println("______O´°>¨`O____");
		System.out.println("");
		System.out.println("Indicar distancia en kilometros a recorrer: ");
		System.out.print("¿Necesita convertir unidades? (Y/N)");
		do {
			m = entrada.nextLine();
		} while (!((m.equals("y") || m.equals("Y") || m.equals("n") || m.equals("N"))));
		if (m.equals("Y") || m.equals("y")) {
			convertirunidades(km,n);
		} else {
			km = Double.parseDouble(entrada.nextLine());
			mostrardistanciabici(km);
		}
	}

	// Mostrar la distancia en automovil/motocicleta
	public static void mostrardistanciaauto(double km) {
		double q;
		// tomando 100km/h como un promedio loq un automovil viaja
		q = km/100;
		System.out.println("Tomando como promedio q se viaja a 100km/h");
		System.out.println("Tu timepo a recorrer en automovil/motocicleta es de:"+Math.round(q)+" Horas");
		naftaauto(q);
	}

	// Opcion en Automovil/motocicleta
	public static void enautomovil(int n) throws IOException {
		double km;
		String m;
		km = 0;
		System.out.println(""); // no hay forma directa de borrar la consola en Java
		System.out.println(" ---  EN AUTOMOVIL  ---");
		System.out.println("");
		System.out.println("       <====~___       ");
		System.out.println("_______¨O-----O´_______");
		System.out.println("");
		System.out.println("Indicar distancia en kilometros a recorrer: ");
		do {
			System.out.print("¿Necesita convertir unidades? (Y/N)");
			m = entrada.nextLine();
		} while (!((m.equals("y") || m.equals("Y") || m.equals("n") || m.equals("N"))));
		System.out.print("Kilomentros: ");
		if (m.equals("Y") || m.equals("y")) {
			convertirunidades(km,n);
		} else {
			km = Double.parseDouble(entrada.nextLine());
			mostrardistanciaauto(km);
		}
	}

	// Mostrar la distancia en barco
	public static void mostrardistanciabarco(double km) {
		double q;
		// tomando 20 nudos como un promedio de un barco
		q = km/1.852;
		System.out.println("Tu tiempo a recorrer en barco es de:"+Math.round(q)+" Horas");
		naftabarco(q);
	}

	// Opcion en Barco
	public static void enbarco(int n) throws IOException {
		double km;
		String m;
		km = 0;
		System.out.println(""); // no hay forma directa de borrar la consola en Java
		System.out.println("---  EN BARCO  --- ");
		System.out.println("");
		System.out.println("      __/\\__");
		System.out.println(" ~~~~~\\____/~~~~");
		System.out.println(" ~~~~~~~~~~~~~~~");
		System.out.println("");
		System.out.println("Indicar distancia en kilometros a recorrer: ");
		System.out.print("¿Necesita convertir unidades? (Y/N)");
		// comprobacion para que solo se ingrese y o n
		do {
			m = entrada.nextLine();
		} while (!((m.equals("y") || m.equals("Y") || m.equals("n") || m.equals("N"))));
		System.out.print("Kilomentros: ");
		if (m.equals("Y") || m.equals("y")) {
			convertirunidades(km,n);
		} else {
			km = Double.parseDouble(entrada.nextLine());
			mostrardistanciabarco(km);
		}
	}

	// Mostrar distancia a recorrer en avion
	public static void mostrardistanciaavion(double km) {
		double q;
		// tomando 900km/h como un promedio de un avion comercial
		q = km/900;
		System.out.println("Tomando como promedio q un avion comercial viaja en 800 y 1000 km/h");
		System.out.println("Tu tiempo a recorrer en avion es de:"+Math.round(q)+" Horas");
		querosenoavion(q);
	}

	// Opcion en Avion
	public static void enavion(int n) throws IOException {
		double km;
		String m;
		km = 0;
		System.out.println(""); // no hay forma directa de borrar la consola en Java
		System.out.println(" ---  EN AVION  ---");
		System.out.println("");
		System.out.println("       __|__");
		System.out.println("------oo(_)oo------");
		System.out.println("");
		System.out.println("Indicar distancia en kilometros a recorrer: ");
		System.out.print("¿Necesita convertir unidades? (Y/N)");
		do {
			m = entrada.nextLine();
		} while (!((m.equals("y") || m.equals("Y") || m.equals("n") || m.equals("N"))));
		if (m.equals("Y") || m.equals("y")) {
			convertirunidades(km,n);
		} else {
			km = Double.parseDouble(entrada.nextLine());
			mostrardistanciaavion(km);
		}
	}

	public static void aguaapie(double q) {
		double litros;
		// 'q' es el timepo q tarda en recorrer x distancia
		litros = 0;
		if (q>=60) {
			do {
				q = q-60;
				litros = litros+1;
			} while (q>60);
			System.out.println("Tomando en cuenta que necesitas entre 500 y 1.000 mililitros cada 1km aproximandamente");
			System.out.println("Necesitarias "+litros+" litros de agua por la distancia dada.");
		} else {
			System.out.println("Necesitaras 500 ml de agua por la distancia dada.");
		}
	}
	//Calculo de cuanta agua tomara segun la distancia ingresada.
	public static void aguaabici(double q) {
		double agua;
		agua = q*9;
		System.out.println("Necesitarias "+agua+" mililitros de agua por la distancia dada.");
	}
	//Calculo de cuanta nafta gastara segun la velocidad y la distancia ingresaga.
	//Y cuanto denero gastara segun que nafta usara.
	public static void naftaauto(double q) {
		double nafta;
		double opcion;
		double opcion_dos;
		double precio;
		System.out.println("Ingrese la velocidad dada:(km/h)");
		opcion = Double.parseDouble(entrada.nextLine());
		if (opcion<=100) {
			nafta = q*5;
			System.out.println("Necesitas alrededor de "+nafta+" litros de nafta por la distancia dada.");
			System.out.println("Elija una opcion:");
			System.out.println("1.Nafta Super");
			System.out.println("2.Nafta Infinia");
			System.out.println("3.Nafta Ultra Diesel");
			System.out.println("4.Nafta Infinia Di�sel");
			opcion_dos = Double.parseDouble(entrada.nextLine());
			if (opcion_dos==1) {
				precio = nafta*111;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
			if (opcion_dos==2) {
				precio = nafta*133;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
			if (opcion_dos==3) {
				precio = nafta*104;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
			if (opcion_dos==4) {
				precio = nafta*127;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
		} else {
			nafta = q*6;
			System.out.println("Necesitas alrededor de "+nafta+" litros de nafta por la distancia dada.");
			opcion_dos = Double.parseDouble(entrada.nextLine());
			if (opcion_dos == 1) {
				precio = nafta*111;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
			if (opcion_dos==2) {
				precio = nafta*133;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
			if (opcion_dos==3) {
				precio = nafta*104;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
			if (opcion_dos==4) {
				precio = nafta*127;
				System.out.println("Gastara $"+precio+" pesos Argentinos.");
			}
		}
	}
	//Calculo de cuanta nafta usara el barco, segun la distancia y cuanto gastara en la nafta.
	public static void naftabarco(double q) {
		double combustible;
		double precio;
		combustible = q*700;
		// Precio del combustible actualizado 11/03/22
		precio = combustible*1;
		System.out.println("Necesitas alrededor de "+combustible+" litros de conbustible por la distancia dada y le costara "+precio+" euros.");
	}
	//Calculo de cuanto queroseno y dinero gastara. 
	public static void querosenoavion(double q) {
		double precio;
		double queroseno_galones;
		double queroseno_litros;
		queroseno_galones = q*3600;
		queroseno_litros = q*14400;
		// Precio actializado 18/04/22
		precio = queroseno_galones*3;
		System.out.println("Necesitas alrededor de "+queroseno_galones+" galones o "+queroseno_litros+" litros de queroseno por la distancia dada y le costara "+precio+" dolares por los galones dados.");
	}
	//Animacion de la opcion apie.
	public static void animacionpie(int n) throws InterruptedException {
		int i;
		// usamos 'i' como un auxiliar para el bucle de repetir
		i = 0;
		do {
			System.out.println("");
			System.out.println("");
			System.out.println("       O    ");
			System.out.println("      / V  ");
			System.out.println("    ./.>... ");
			Thread.sleep(300);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("");
			System.out.println("");
			System.out.println("       O    ");
			System.out.println("      /    ");
			System.out.println("  ...V.\\   ");
			Thread.sleep(75);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("");
			System.out.println("");
			System.out.println("       O    ");
			System.out.println("    / /    ");
			System.out.println("  ...V.\\   ");
			Thread.sleep(300);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			i = i+1;
		} while (i!=5);
	}
	//Animacion de la opcion bici.
	public static void animacionbici(int n) throws InterruptedException {
		int i;
		// usamos 'i' como un auxiliar para el bucle de repetir
		i = 0;
		do {
			System.out.println("");
			System.out.println("");
			System.out.println("  o     ");
			System.out.println("..|<} ........");
			System.out.println("O´°>¨`O ");
			System.out.println("//////////////");
			Thread.sleep(400);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("");
			System.out.println("");
			System.out.println("     o     ");
			System.out.println(".....|<} .....");
			System.out.println("   O´°>¨`O ");
			System.out.println("//////////////");
			Thread.sleep(400);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("");
			System.out.println("");
			System.out.println("        o     ");
			System.out.println("........|<} ..");
			System.out.println("      O´°>¨`O ");
			System.out.println("//////////////");
			Thread.sleep(400);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			i = i+1;
		} while (i!=5);
	}
	//Animacion de la opcion auto.
	public static void animacionauto(int n) throws InterruptedException {
		int i;
		// usamo 'i' como un auxiliar para el bucle de repetir
		i = 0;
		do {
			System.out.println("");
			System.out.println("");
			System.out.println("           ......");
			System.out.println("   <====~___     ");
			System.out.println("    ¨O-----O´    ");
			System.out.println("/////////////////");
			Thread.sleep(150);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("");
			System.out.println("");
			System.out.println("    ...........  ");
			System.out.println("   <====~___     ");
			System.out.println("    ¨O-----O´    ");
			System.out.println("/////////////////");
			Thread.sleep(150);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("");
			System.out.println("");
			System.out.println("......           ");
			System.out.println("   <====~___     ");
			System.out.println("    ¨O-----O´    ");
			System.out.println("/////////////////");
			Thread.sleep(150);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			i = i+1;
		} while (i!=6);
	}
	//Animacion de la opcion barco.
	public static void animacionbarco(int n) throws InterruptedException {
		int i;
		// usamo 'i' como un auxiliar para el bucle de repetir
		i = 0;
		do {
			System.out.println("               ____     ");
			System.out.println("              /~~~~|    ");
			System.out.println("         ____/~~~~~~ |__");
			System.out.println("         \\             |");
			System.out.println("~~~~~~~~~~\\____________/");
			System.out.println("~~~~~~~~~~~~~~~~~~~~~~~~");
			Thread.sleep(400);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("          ____     ");
			System.out.println("         /~~~~|    ");
			System.out.println("    ____/~~~~~~ |__");
			System.out.println("    \\             |");
			System.out.println("~~~~~\\____________/~~~~~");
			System.out.println("~~~~~~~~~~~~~~~~~~~~~~~~");
			Thread.sleep(400);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("     ____     ");
			System.out.println("    /~~~~|    ");
			System.out.println("___/~~~~~~ |__");
			System.out.println("             |");
			System.out.println("\\____________/~~~~~~~~~~");
			System.out.println("~~~~~~~~~~~~~~~~~~~~~~~~");
			Thread.sleep(400);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			i = i+1;
		} while (i!=5);
	}
	//Animacion de la opcion avio.
	public static void animacionavion(int n) throws InterruptedException {
		int i;
		// usamo 'i' como un auxiliar para el bucle de repetir
		i = 0;
		do {
			System.out.println("                    ......");
			System.out.println("                ^ ____    ");
			System.out.println("               /  \\___|   ");
			System.out.println("     /\\......./    \\      ");
			System.out.println("    <´               }    ");
			System.out.println("     \\/´´´´´´´\\    /__    ");
			System.out.println("               \\  /___|   ");
			System.out.println("                v         ");
			System.out.println("                    ......");
			Thread.sleep(150);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("          .............   ");
			System.out.println("                ^ ____    ");
			System.out.println("               /  \\___|   ");
			System.out.println("     /\\......./    \\      ");
			System.out.println("    <´               }    ");
			System.out.println("     \\/´´´´´´´\\    /__    ");
			System.out.println("               \\  /___|   ");
			System.out.println("                v         ");
			System.out.println("              ............");
			Thread.sleep(150);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("..........            ....");
			System.out.println("                ^ ____    ");
			System.out.println("               /  \\___|   ");
			System.out.println("     /\\......./    \\      ");
			System.out.println("    <´               }    ");
			System.out.println("     \\/´´´´´´´\\    /__    ");
			System.out.println("               \\  /___|   ");
			System.out.println("                v         ");
			System.out.println("   ............           ");
			Thread.sleep(150);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			i = i+1;
		} while (i!=6);
	}
	//Animacion de la opcion tren.
	public static void animaciontren(int n) throws InterruptedException {
		int i;
		// usamo 'i' como un auxiliar para el bucle de repetir
		i = 0;
		// la animacion del tren fue vastante costosa
		do {
			System.out.println("                                             ");
			System.out.println("   _   _   _   _                             ");
			System.out.println("  _______        \\                           ");
			System.out.println(" | |---| |     |_  _|                        ");
			System.out.println(" |_|___|-|______|  |___                      ");
			System.out.println(" |  -  _    -   _    - |                     ");
			System.out.println(" |-_____  -       -    |]                    ");
			System.out.println(" / \\   / \\ ____________|__                   ");
			System.out.println("|    +    |  ___      ___  \\                 ");
			System.out.println(" \\ /   \\ /==| x |====| x |==\\                ");
			System.out.println(" --=====-----===------===--------------------");
			Thread.sleep(170);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("                                             ");
			System.out.println("  _   _   _   _   _   _                      ");
			System.out.println("          _______        \\                   ");
			System.out.println("         | |---| |     |_  _|                ");
			System.out.println(" _     - | |___| |______|  |___              ");
			System.out.println("   -  _  | -   _    -     -    |             ");
			System.out.println(" -      _| _____ -       -  _  |]            ");
			System.out.println(" -  _  - /   |   \\ ____________|__           ");
			System.out.println(" -    - | -- x -- |  ___      ___  \\         ");
			System.out.println("-   _    \\   |   /==| + |====| + |==\\        ");
			System.out.println("-----------=====-----===------===------------");
			// las particulas de velocidad ,fueron un dolor de cabeza
			Thread.sleep(170);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			System.out.println("                                             ");
			System.out.println("   _   _   _   _   _   _   _   _             ");
			System.out.println("                  _______        \\           ");
			System.out.println("                 | |---| |     |_  _|        ");
			System.out.println("_     -   _  -   | |___| |______|  |___      ");
			System.out.println("  -  _    -   _  | -     -   _    -    |     ");
			System.out.println("-     _         -| _____-  _   -  _    |]    ");
			System.out.println("-  _  -     _    / \\   / \\ ____________|__   ");
			System.out.println("-    -   -      |    +    |  ___      ___  \\ ");
			System.out.println("-  _    -   _    \\ /   \\ /==| x |====| x |==\\");
			System.out.println("-------------------=====-----===------===----");
			Thread.sleep(170);
			System.out.println(""); // no hay forma directa de borrar la consola en Java
			i = i+1;
		} while (i!=6);
	}
	//Calculo de cuanta energuia usara y demas.
	public static void electricidadtren(double q) {
		double electricidad;
		double precio;
		double preciopasaje;
		// esta es la cantidad de kilovatios usados en 280 kh
		electricidad = q*10640;
		// Precio de electricidad es un promedio de los vlores europeos actualizado 18/03/22
		precio = electricidad*0.21;
		// ponemos un promedio de pasajeros para saber el valor del pasaje
		preciopasaje = precio/350;
		System.out.println("Necesitas alrededor de "+electricidad+" kilovatios por hora de electricidad por la distancia dada y le costara al estado "+Math.round(precio)+" euros.");
		System.out.println("Ya que en un viaje comercial hay un promedio de 400 pasajeros, el valor de tu voleto seria de "+Math.round(preciopasaje)+" euros. ");
	}

	// Mostrar distancia a recorrer en tren
	public static void mostrardistanciatren(double km) {
		double q;
		// tomando 280 km/h como un promedio de un tren electrico de pasajeros
		q = km/280;
		System.out.println("Tomando como promedio que un tren electrico de pasajeros viaja en 200 y 300 km/h");
		System.out.println("Tu tiempo a recorrer en tren electrico es de:"+Math.round(q)+" Horas");
		electricidadtren(q);
	}

	// este es el subproseso de la opcion tren
	public static void tren(int n) throws IOException {
		double km;
		String m;
		km = 0;
		System.out.println(""); // no hay forma directa de borrar la consola en Java
		System.out.println("---  EN TREN  ---");
		System.out.println("");
		System.out.println(" ~~~~ __ - ~ ~~~~~~");
		System.out.println(" ~~~~|[]|__I_ ~~~~~");
		System.out.println(" ~~~~|______ p ~~~~");
		System.out.println(" ~~~ [0]~~o~o\\~~~~~");
		System.out.println("");
		System.out.println("Indicar distancia en kilometros a recorrer: ");
		System.out.print("¿Necesita convertir unidades? (Y/N)");
		// comprobacion para que solo se ingrese y o n
		do {
			m = entrada.nextLine();
		} while (!((m.equals("y") || m.equals("Y") || m.equals("n") || m.equals("N"))));
		if (m.equals("Y") || m.equals("y")) {
			convertirunidades(km,n);
		} else {
			km = Double.parseDouble(entrada.nextLine());
			mostrardistanciatren(km);
		}
	}


}

