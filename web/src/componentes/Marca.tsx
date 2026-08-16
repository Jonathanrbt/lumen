/**
 * El logotipo: la lechuza de Atenea y el nombre.
 *
 * La lechuza va como imagen —es pixel art, no hay trazo que vectorizar— y
 * «Lumen» como texto vivo, para que herede el color del tema donde caiga.
 * Sobre fondo oscuro el azul se apaga, así que ahí se aclara.
 */
import marca from '../assets/lumen-marca.png'

const TAMANOS = {
  sm: { ave: 'h-6', nombre: 'text-base', hueco: 'gap-2' },
  md: { ave: 'h-9', nombre: 'text-xl', hueco: 'gap-2.5' },
  lg: { ave: 'h-14', nombre: 'text-3xl', hueco: 'gap-3.5' },
}

export function Marca({ tamano = 'sm' }: { tamano?: keyof typeof TAMANOS }) {
  const t = TAMANOS[tamano]

  return (
    <span className={`inline-flex items-center ${t.hueco}`}>
      <img
        src={marca}
        alt=""
        aria-hidden
        className={`${t.ave} w-auto [.tema-oscuro_&]:brightness-[1.75] [.tema-oscuro_&]:saturate-[0.9]`}
      />
      <span className={`font-serif leading-none ${t.nombre}`}>
        Lumen
        <sup className="ml-px text-[0.42em] align-super">©</sup>
      </span>
    </span>
  )
}
