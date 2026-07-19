// context/ConfirmProvider.jsx
// Monta el diálogo de confirmación y registra su handler en el singleton utils/confirm.js.
import { useState, useCallback, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import ConfirmDialog from '../components/ui/ConfirmDialog/ConfirmDialog';
import { _bindConfirm } from '../utils/confirm';

export function ConfirmProvider({ children }) {
  const [options, setOptions] = useState(null);
  const resolver = useRef(null);

  const open = useCallback((opts) => {
    return new Promise((resolve) => {
      resolver.current = resolve;
      setOptions(opts || {});
    });
  }, []);

  useEffect(() => {
    _bindConfirm(open);
  }, [open]);

  const settle = useCallback((result) => {
    if (resolver.current) resolver.current(result);
    resolver.current = null;
    setOptions(null);
  }, []);

  return (
    <>
      {children}
      {options &&
        createPortal(
          <ConfirmDialog
            {...options}
            onConfirm={() => settle(true)}
            onCancel={() => settle(false)}
          />,
          document.body
        )}
    </>
  );
}

export default ConfirmProvider;
