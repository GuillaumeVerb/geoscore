type Props = { id?: string; children: React.ReactNode };

export function SectionTitle({ id, children }: Props) {
  return (
    <h2 className="sectionTitle" id={id}>
      {children}
    </h2>
  );
}
