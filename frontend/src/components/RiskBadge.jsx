export default function RiskBadge({ level }) {
  const classes = {
    CRITICAL: 'risk-badge-critical',
    HIGH: 'risk-badge-high',
    MEDIUM: 'risk-badge-medium',
    LOW: 'risk-badge-low',
    UNASSESSED: 'risk-badge-unassessed',
  };
  return <span className={classes[level] || classes.UNASSESSED}>{level}</span>;
}
