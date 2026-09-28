const DEPARTMENT_STYLES = {
  'PWD (Arterial Roads)': 'border-blue-500/30 bg-blue-500/10 text-blue-300',
  'Ward Local Maintenance': 'border-green-500/30 bg-green-500/10 text-green-300',
  'Traffic Police Safety': 'border-orange-500/30 bg-orange-500/10 text-orange-300',
};

export default function DepartmentBadge({ departmentName }) {
  const label = departmentName || 'Department unassigned';
  const style = DEPARTMENT_STYLES[label] || 'border-gray-600 bg-gray-800 text-gray-300';
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${style}`}>
      {label}
    </span>
  );
}
