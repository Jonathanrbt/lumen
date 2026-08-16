/**
 * Desfile de las fuentes con las que trabaja el motor.
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
import legalize from '../assets/marcas/legalize.png'
import procuraduria from '../assets/marcas/procuraduria.png'
import rues from '../assets/marcas/rues.png'
import secop from '../assets/marcas/secop.png'
import sicaac from '../assets/marcas/sicaac.png'
import supersociedades from '../assets/marcas/supersociedades.png'

const MARCAS = [
  { nombre: 'Croma', src: croma },
  { nombre: 'SECOP I y II', src: secop },
  { nombre: 'RUES', src: rues },
  { nombre: 'Supersociedades', src: supersociedades },
  { nombre: 'SICAAC', src: sicaac },
  { nombre: 'Procuraduría', src: procuraduria },
  { nombre: 'Contraloría', src: contraloria },
  { nombre: 'Contaduría General', src: contaduria },
  { nombre: 'Legalize', src: legalize },
  { nombre: 'ANCP-CCE', src: ancpCce },
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
                className="h-11 w-auto opacity-65 transition-opacity duration-300 hover:opacity-100"
              />
            </li>
          )
        })}
      </ul>
    </div>
  )
}
