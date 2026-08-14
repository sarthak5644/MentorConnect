import { useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Upload } from 'lucide-react';
import { mentorsApi } from '@/api/endpoints';
import { DocumentStatus, MentorDocument } from '@/types';
import { PageSpinner, EmptyState, Badge, Button, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { formatDate } from '@/lib/utils';

const statusVariant: Record<DocumentStatus, 'default' | 'success' | 'warning' | 'danger'> = {
  [DocumentStatus.PENDING]: 'warning',
  [DocumentStatus.VERIFIED]: 'success',
  [DocumentStatus.REJECTED]: 'danger',
};

export default function MentorDocuments() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: documents, isLoading } = useQuery<MentorDocument[]>({
    queryKey: ['mentor-documents'],
    queryFn: mentorsApi.getMyDocuments,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => {
      const fd = new FormData();
      fd.append('file', file);
      return mentorsApi.uploadDocument(fd, 'ID_PROOF');
    },
    onSuccess: () => {
      showToast('Document uploaded', 'success');
      qc.invalidateQueries({ queryKey: ['mentor-documents'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div className="max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Verification documents</h1>
        <input ref={fileRef} type="file" className="hidden" onChange={(e) => e.target.files?.[0] && uploadMutation.mutate(e.target.files[0])} />
        <Button size="sm" onClick={() => fileRef.current?.click()} isLoading={uploadMutation.isPending}>
          <Upload className="h-4 w-4" /> Upload
        </Button>
      </div>

      {!documents?.length ? (
        <div className="mt-6">
          <EmptyState icon={FileText} title="No documents uploaded" description="Upload ID proof or credentials for admin verification." />
        </div>
      ) : (
        <div className="mt-6 space-y-3">
          {documents.map((d) => (
            <div key={d.id} className="session-card flex items-center justify-between">
              <div>
                <p className="font-medium text-ink-800 dark:text-ink-50">{d.file_name}</p>
                <p className="text-xs text-ink-400">{d.document_type} · {formatDate(d.created_at)}</p>
                {d.rejection_reason && <p className="text-xs text-danger mt-1">{d.rejection_reason}</p>}
              </div>
              <Badge variant={statusVariant[d.status]}>{d.status}</Badge>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
