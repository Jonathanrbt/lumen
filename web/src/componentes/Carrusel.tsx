/**
 * Desfile de las fuentes con las que trabaja el motor.
 *
 * Las marcas van a una sola tinta y a un alto óptico parejo, para que la tira
 * no se vuelva un muestrario de colores institucionales.
 *
 * La tira va dos veces y se desplaza media anchura: cuando la primera copia
 * termina de salir, la segunda está justo donde empezó la primera. El aire va
 * como relleno de cada marca y no como `gap`, o entre las dos copias quedaría
 * un hueco de más y el salto se vería.
 */
import ancpCce from '../assets/marcas/ancp-cce.png'
import contaduria from '../assets/marcas/contaduria.png'
import contraloria from '../assets/marcas/contraloria.png'
import croma from '../assets/marcas/croma.png'
import procuraduria from '../assets/marcas/procuraduria.png'
import rues from '../assets/marcas/rues.png'
import secop from '../assets/marcas/secop.png'
import sicaac from '../assets/marcas/sicaac.png'

const MARCAS = [
  { nombre: 'Croma', src: croma },
  { nombre: 'SECOP I y II', src: secop },
  { nombre: 'RUES', src: rues },
  { nombre: 'SICAAC', src: sicaac },
  { nombre: 'Procuraduría General de la Nación', src: procuraduria },
  { nombre: 'Contraloría General de la República', src: contraloria },
  { nombre: 'Contaduría General de la Nación', src: contaduria },
  { nombre: 'Agencia Nacional de Contratación Pública', src: ancpCce },
]

export function Carrusel() {
  return (
    <div
      className="group relative overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_7%,black_93%,transparent)]"
      aria-label="Fuentes oficiales que consulta el motor"
    >
      <ul className="flex w-max animate-[desfile_42s_linear_infinite] group-hover:[animation-play-state:paused] motion-reduce:animate-none">
        {[...MARCAS, ...MARCAS].map((marca, i) => {
          const copia = i >= MARCAS.length
          return (
            <li key={i} className="shrink-0 pr-14 sm:pr-20" aria-hidden={copia}>
              <img
                src={marca.src}
                alt={copia ? '' : marca.nombre}
                className="h-12 w-auto opacity-70 transition-opacity duration-300 hover:opacity-100"
              />
            </li>
          )
        })}
      </ul>
    </div>
  )
}
