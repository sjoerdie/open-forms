import React from 'react';
import PropTypes from 'prop-types';
import {FormattedMessage, useIntl} from 'react-intl';

import Field from '../forms/Field';
import FormRow from '../forms/FormRow';
import Fieldset from '../forms/Fieldset';
import Select from "../forms/Select";
import Form from "@rjsf/core";


const RegistrationFields = ({
    backends=[],
    selectedBackend='',
    backendOptions={},
    backendOptionsForms={},
    onChange,
}) => {
    const intl = useIntl();
    const backendChoices = backends.map( backend => [backend.id, backend.label]);
    const optionsFormSchema = backendOptionsForms[selectedBackend];

    const addAnotherMsg = intl.formatMessage({
        description: 'Button text to add extra item',
        defaultMessage: 'Add another',
    });

    return (
        <Fieldset style={{
            '--of-add-another-text': `"${addAnotherMsg}"`
        }}>
            <FormRow>
                <Field
                    name="form.registrationBackend"
                    label={<FormattedMessage defaultMessage="Select registration backend" description="Registration backend label" />}
                >
                    <Select
                        choices={backendChoices}
                        value={selectedBackend}
                        onChange={(event) => {
                            onChange(event);
                            // Clear options when changing backend
                            onChange({target: {name: 'form.registrationBackendOptions', value: {}}})
                        }}
                        allowBlank={true}
                    />
                </Field>
            </FormRow>
            {optionsFormSchema
                ? (<FormRow>
                    <Field
                        name="form.registrationBackendOptions"
                        label={<FormattedMessage defaultMessage="Registration backend options" description="Registration backend options label" />}
                    >
                        <Form
                            schema={optionsFormSchema}
                            formData={backendOptions}
                            onChange={({ formData }) => onChange({target: {name: 'form.registrationBackendOptions', value: formData}})}
                            children={true}
                        />
                    </Field>
                </FormRow> )
                : null
            }
        </Fieldset>
    );
};

RegistrationFields.propTypes = {
    backends: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired,
    })),
    selectedBackend: PropTypes.string,
    backendOptions: PropTypes.object,
    backendOptionsForms: PropTypes.objectOf(PropTypes.shape({
        type: PropTypes.oneOf(['object']), // it's the JSON schema root, it has to be
        properties: PropTypes.object,
        required: PropTypes.arrayOf(PropTypes.string),
    })),
    onChange: PropTypes.func.isRequired,
};


export default RegistrationFields;
