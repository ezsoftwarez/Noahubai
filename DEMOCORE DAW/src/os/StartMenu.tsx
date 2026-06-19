import { APPS } from "./apps";
import type { AppId } from "./types";

interface Props {
  onOpen: (appId: AppId) => void;
  onClose: () => void;
}

export default function StartMenu({ onOpen, onClose }: Props) {
  return (
    <div className="start-menu" onClick={(e) => e.stopPropagation()}>
      <h3>Alkalmazások</h3>
      <div className="start-menu-grid">
        {APPS.map((app) => (
          <button
            key={app.id}
            type="button"
            className="start-menu-item"
            onClick={() => {
              onOpen(app.id);
              onClose();
            }}
          >
            <span>{app.icon}</span>
            <span>{app.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
